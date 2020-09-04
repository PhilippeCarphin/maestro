
"""
Functions for dealing with maestro XML files.
"""
import os
import os.path
import re
from copy import deepcopy

import lxml
from lxml import etree
from utilities.pretty import pretty, pprint_kwargs
from utilities.xml import xml_cache
from utilities.io import safe_open
from home_logger import logger
from constants import NODE_TYPES, CONTAINER_TAGS

"A regex where group(1) is the contents of the 'catchup' attribute."
CATCHUP_XML_REGEX = re.compile(r"""[ ]+catchup[ ]*=[ ]*["']([^'"]*)["']""")


def has_empty_inner_modules(element):
    """
    Returns true if this element contains empty <MODULE> elements.
    This means this element requires some of its children to be 
    replaced by the full <MODULE> found elsewhere.
    """

    return (bool)(get_empty_inner_modules(element))


def is_empty_module(element):
    return not element_has_node_children(element) and is_module(element)


def is_element(item):
    return type(item) is lxml.etree._Element


def get_empty_inner_modules(element):

    inner_modules = element.xpath(".//MODULE")

    return [i for i in inner_modules if i != element and not element_has_node_children(i)]


def is_module(element):
    return type(element) is lxml.etree._Element and element.tag.lower() == "module"


def is_container(item):
    """
    item can be an element, tag string, or NODE_TYPE
    """
    key = item
    if is_element(item):
        key = item.tag.lower()
    return key in CONTAINER_TAGS


def get_closest_container(element):
    """
    Returns the closest container element containing this element.
    """

    for a in get_ancestors(element, include_self=False):
        if a.tag.lower() in CONTAINER_TAGS:
            return a

    return None


def get_closest_module(element):
    """
    Returns the closest module element containing this element.
    For example: element1 in module1 in module2, given element1 returns module1.
    """

    for a in get_ancestors(element):
        if a.tag.lower() == "module":
            return a

    return None


def get_ancestors(element, include_self=True):
    "return a list of elements [child, parent, grandparent, ...] up to the root."

    if include_self:
        ancestors = [element]
    else:
        ancestors = []

    while element.getparent() != element:
        element = element.getparent()
        if element is None:
            break
        ancestors.append(element)
    return ancestors


def get_flow_branch_from_flow_element(element):
    """
    Given any element in a flow XML, returns the flow_branch (not node_path).
    This is the path you visually see in a xflow or mflow visualization.

    Often, this does not follow the structure of the XML leaf to root, instead it
    jumps around to different elements, tracing back to the root eventually.
    """

    container_element = get_closest_container(element)

    if container_element is None:
        return element.attrib["name"]

    "If element is not <SUBMITS>, find its <SUBMITS> partner, set element to that."
    is_submit = element.tag.lower() == "submits"
    if not is_submit:

        if element.tag.lower() not in NODE_TYPES:
            "non-flow elements like <DEPENDS_ON> have no flow_branch"
            return ""

        name = element.attrib["name"]
        xpath = ".//SUBMITS[@sub_name='%s']" % name
        query = container_element.xpath(xpath)
        if not query:
            return element.attrib.get("name", "")
        element = query[0]

    submit_element = element

    parent = submit_element.getparent()
    sub_name = submit_element.attrib.get("sub_name", "")
    before = get_flow_branch_from_flow_element(parent)

    return before+"/"+sub_name


def get_node_path_from_flow_element(element,
                                    inner_module_path=False):
    """
    Finds the 'sub_name' or 'name' for this element.
    Constructs the node_path (used by maestro utilities) for that name in its module.   

    If inner_module_path, recursion stops at the first module instead of the root.
    This is used to construct the paths within the "$SEQ_EXP_HOME/modules" folder.

    Returns two node paths - with and without switch indexes:
        module1/switch1/00/task1
        module1/switch1/task1
    (node_path, no_index_node_path)
    """

    is_submit = element.tag.lower() == "submits"
    if is_submit:
        name = element.attrib.get("sub_name", "")
        xpath = ".//*[@name='%s']" % name
        container_element = get_closest_container(element)
        results = container_element.xpath(xpath)
        if not results:
            return "", ""

        """
        Sometimes the root module name matches another child task element.
        Remove the module from results.
        """
        results = [e for e in results if e != container_element]

        element = results[0]

    if element.tag.lower() not in NODE_TYPES:
        "non-flow elements like <DEPENDS_ON> have no node_path"
        return "", ""

    node_path = ""
    no_index_node_path = ""
    parent = element
    while parent is not None:

        is_switch = parent.tag == "SWITCH_ITEM"
        node_path = parent.attrib["name"]+"/"+node_path
        if not is_switch:
            no_index_node_path = parent.attrib["name"]+"/"+no_index_node_path

        if inner_module_path and is_module(parent):
            break

        parent = parent.getparent()

    "remove trailing slash"
    node_path = node_path[:-1]
    no_index_node_path = no_index_node_path[:-1]

    return node_path, no_index_node_path


def get_module_name_for_element(element):
    return get_closest_module(element).attrib.get("name", "")


def get_paths_from_element(element):
    """
    Returns (flow_branch, node_path, no_index_node_path, module_path_inner)
    """
    flow_branch = get_flow_branch_from_flow_element(element)
    node_path, no_index_node_path = get_node_path_from_flow_element(element)
    _, module_path = get_node_path_from_flow_element(element, inner_module_path=True)
    return flow_branch, node_path, no_index_node_path, module_path


def get_module_name_from_flow_xml(path):
    "Given a flow xml, returns the 'name' of the top module element."
    root = xml_cache.get(path)
    if root is None:
        return ""
    return root.get("name")


def get_submits_from_flow_element(element):
    """
    Returns a list of all node_path for every <SUBMITS> child of this element.
    """
    submit_children = [child for child in element if child.tag.lower() == "submits"]
    result = [get_node_path_from_flow_element(child)[0] for child in submit_children]
    return [i for i in result if i]


def get_flow_children_from_flow_element(element):
    """
    Returns a list of all children (node_path) that should be 
    visible in a flow visualization.
    """

    result = []
    for child in element:
        tag = child.tag.lower()
        if tag in ("submits", "switch_item"):
            node_path = get_node_path_from_flow_element(child)[0]
            result.append(node_path)
        elif tag == "npass_task":
            """
            An <NPASS_TASK> with no matching <SUBMITS> element is still shown in the flow,
            In that case, act as if there were a <SUBMITS> right next to the <NPASS_TASK>.
            """
            container = get_closest_container(child)
            npt_name = child.attrib.get("name")
            if not npt_name:
                continue
            xpath = ".//SUBMITS[@sub_name='%s']" % npt_name
            search = container.xpath(xpath)
            if not search:
                node_path = get_node_path_from_flow_element(child)[0]
                result.append(node_path)

    return [i for i in result if i]


def get_node_type_from_element(element):
    "this extra None checking, instead of simply 'if not element' avoids lxml FutureWarning"
    if element is None:
        return ""
    if type(element) is not lxml.etree._Element and not element:
        return ""

    tag = element.tag.lower()
    if tag in NODE_TYPES:
        return tag

    return ""


def find_all_flow_xml_for_experiment(path):
    """
    Returns a list of full paths to all flow xml files for this experiment.
    The EntryModule is first.
    """

    paths = []
    modules_folder = path+"modules/"
    entry_module = os.path.realpath(path+"EntryModule")

    if not os.path.isdir(modules_folder):
        logger.error("No modules folder in experiment '%s'" % path)
        return []

    for module in os.listdir(modules_folder):
        xml = modules_folder+module+"/flow.xml"
        if os.path.isfile(xml):
            if entry_module.endswith(module):
                paths.insert(0, os.path.abspath(xml))
            else:
                paths.append(os.path.abspath(xml))

    return paths


def get_combined_flow_for_experiment_path(experiment_path, verbose=False):
    xml_flows = find_all_flow_xml_for_experiment(experiment_path)
    return get_combined_flow_from_paths(xml_flows, verbose=verbose)


def get_combined_flow_from_paths(xml_paths, verbose=False):
    """
    Insert the contents of all these XMLs into the first according to maestro flow rules.

    Sometimes a flow XML will have a "SUBMITS" element, but the matching "MODULE" element with a matching sub_name is found in another XML.
    This returns an lxml root that combines them all, as if they were all in one XML.
    """
    assert type(xml_paths) in (list, tuple)

    xml_text_list = []
    for path in xml_paths:

        if not os.path.isfile(path):
            continue

        xml_data = safe_open(path)

        "xflow ignores 'name' in <MODULE> and uses module folder instead"
        module_folder = path.split("/")[-2]
        xml_data = replace_module_name(xml_data, module_folder)

        xml_text_list.append(xml_data)

    return get_combined_flow_from_text_list(xml_text_list, verbose=verbose)


def replace_module_name(xml_data, module_name):
    """
    In most cases, xflow ignores the 'name' attribute in <MODULE> elements,
    instead it uses the folder containing the flow.xml

    To reproduce this behaviour, this finds the first <MODULE> element and 
    replaces its 'name' with module_name
    """

    assert type(xml_data) is str

    try:
        tree = etree.fromstring(xml_data, parser=etree.XMLParser(remove_comments=True))
    except etree.XMLSyntaxError:
        logger.error("lxml failed to replace module name for module: '%s'" % module_name)
        return xml_data

    for element in tree.iter():
        if is_module(element):
            element.attrib["name"] = module_name
            return etree.tostring(element).decode()

    logger.error("lxml failed to replace module name for module: '%s'" % module_name)
    return xml_data


def element_has_node_children(element):
    """
    Returns true if this element contains SUBMITS or any node type children.
    Excludes <DEPENDS_ON> elements.
    """

    for child in element:
        tag = child.tag.lower()
        if tag == "submits":
            return True
        if tag in NODE_TYPES:
            return True
    return False


def get_module_elements_cached(element):
    "find all module elements, either this root element, or any elements inside it"
    return element.xpath("//MODULE")


def get_combined_flow_from_text_list(xml_datas, verbose=False):
    "assume first xml_data is the main flow xml"

    assert type(xml_datas) in (list, tuple)
    assert xml_datas
    assert type(xml_datas[0]) is str

    "the main root flow element"
    main_flow = None

    """
    Modules which contain no empty modules.
    These modules are guaranteed not to change and can be deep copied.
    Key is a module_name string, value is an lxml root for that module element.
    """
    complete_modules = {}

    """
    All modules which contain empty modules.
    These modules still need to be fixed, by replacing the empty module child with a complete module.
    """
    incomplete_modules = []

    for text in xml_datas:

        try:
            root = etree.fromstring(text, parser=etree.XMLParser(remove_comments=True))
        except etree.XMLSyntaxError:
            logger.error("lxml failed to parse text: '%s'" % text[:50])
            continue

        module_elements = xml_cache.get_elements_of_tag(root, "MODULE")

        "map module_name to module_element"
        for module_element in module_elements:

            module_name = module_element.attrib.get("name")
            if not module_name:
                continue

            if main_flow is None:
                main_flow = module_element

            if has_empty_inner_modules(module_element):
                incomplete_modules.append(module_element)
            elif not is_empty_module(module_element):
                complete_modules[module_name] = module_element

    """
    Use complete modules to fill in the incomplete modules.
    """
    made_progress = True
    while made_progress:

        made_progress = False

        "[:] makes a new list for iteration so we can remove items from it as we go"
        for incomplete in incomplete_modules[:]:
            children = get_empty_inner_modules(incomplete)
            children_names = [child.attrib.get("name") for child in children]

            "if any of the children modules are incomplete, we cannot yet fill in this module"
            if any([name not in complete_modules for name in children_names]):
                continue

            for child in children:
                child_name = child.attrib["name"]
                parent = child.getparent()
                index = parent.index(child)
                parent.remove(child)
                """
                deepycopy because lxml insert will also remove any 
                elements, anywhere, with the same reference.
                """
                complete = deepcopy(complete_modules[child_name])
                if is_empty_module(complete):
                    pprint_kwargs(child_name=child_name,
                                  complete=complete,
                                  parent=parent,
                                  incomplete=incomplete)
                    raise ValueError("refusing to insert incomplete module")

                parent.insert(index, complete)

            incomplete_modules.remove(incomplete)

            if not is_empty_module(incomplete):
                iname = incomplete.attrib["name"]
                complete_modules[iname] = incomplete

            made_progress = True

    if incomplete_modules:
        message = "\n\n".join([pretty(m) for m in incomplete_modules])
        logger.error("combine flow XML failed to resolve all modules containing empty module children. incomplete_modules =\n"+message)

    return main_flow
