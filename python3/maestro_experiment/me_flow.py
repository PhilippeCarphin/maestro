
"""
This code handles flow reading for the MaestroExperiment class.

This abstract class is not meant to be instantiated, only inherited.
"""

import os.path
import lxml

from maestro.datestamp import get_day_of_week
from constants import NODE_TYPE, SWITCH_TYPE
from maestro.xml import get_combined_flow_for_experiment_path, get_node_type_from_element, get_submits_from_flow_element, \
    get_flow_children_from_flow_element, get_module_name_from_flow_xml, get_paths_from_element, get_module_name_for_element, is_container
from utilities.pretty import pretty_kwargs
from utilities.parsing import superstrip
from home_logger import logger


class ME_Flow():

    def inspect_flow(self):
        "Crawl the experiment files to build the flow data."

        "key is node_path string, value is node_data dictionary"
        self.node_path_to_node_data = {}

        "key is a module name, value is an lxml parsed tree object"
        self.module_name_to_tree = {}

        """
        flow_datas key is any node_path, value is flow_data
        
        flow_data = {"flow_children_node_paths": [node_path1, node_path2, ...],
                     "submits_children_node_paths": [node_path1, node_path2, ...],
                     "type": NODE_TYPE,
                     "flow_branch": path_in_modules_folder }        
        
        "flow_children_node_paths" and "submits_children_node_paths" often overlap, but not always, for example npasstasks
        """
        self.flow_datas = {}

        """
        key is node_path, value is node_data
        this is a cache, use functions to retrieve node_data
        """
        self.node_datas = {}

        """
        key is node_path, value is NODE_TYPE
        """
        self.node_types = {}
        
        """
        list of all container elements in the flow which are containers
        like loop, switch, family, module
        """
        self.container_elements=[]

        """
        key is node_path of child, value is node_path of parent in the visual flow
        """
        self.flow_child_to_parent = {}

        """
        key is a node path used internally by mflow, including switch indexes like:
            module1/switch1/00/task1
            module1/switch1/12/task2
        value is the node path understood by xflow and used to construct resource xml paths:
            module1/switch1/task1
            module1/switch1/task2
        """
        self.node_path_to_no_index_node_path = {}

        self.build_flow_data()

    def build_flow_data(self):
        "Build the flow_data for each node using the parsed XML flow files."

        self.root_flow_branch = None
        self.root_module_name = None
        self.root_node_path = None
        self.root_flow = None
        self.root_node_data = None

        entry_flow = self.path+"EntryModule/flow.xml"
        self.root_flow_branch = os.path.abspath(entry_flow)
        self.root_module_name = get_module_name_from_flow_xml(entry_flow)

        if not self.root_module_name:
            logger.warning("Failed to find root module name in flow.xml: '%s'" % entry_flow)
            return

        self.root_node_path = self.root_module_name
        self.root_flow = get_combined_flow_for_experiment_path(self.path)

        if self.root_flow is None:
            logger.warning("Failed to find root flow element in flow.xml: '%s'" % entry_flow)
            return

        self.container_elements.append(self.root_flow)
        
        "exclude non-elements in document, like comments"
        children = [child for child in self.root_flow.iter() if type(child) is lxml.etree._Element]

        for child in children:
            self.process_flow_element(child)

        self.root_node_data = self.get_node_data(self.root_module_name)

    def is_node_path(self, node_path):
        if self.has_critical_errors:
            return False
        return node_path in self.node_path_to_no_index_node_path.values()

    def process_flow_element(self, element):
        """
        Process an element from a flow XML.
        Travel up through its ancestors to get node_data info and paths for config, resources, task, etc.
        """

        flow_branch, node_path, no_index_node_path, module_path = get_paths_from_element(element)
        node_type = get_node_type_from_element(element)
        
        if is_container(element):
            self.container_elements.append(element)

        self.node_path_to_no_index_node_path[node_path] = no_index_node_path

        module_name = module_path.split("/")[0]
        flow_path = self.path+"modules/"+module_name+"/flow.xml"

        "if the node_type is unknown, like <DEPENDS_ON> then ignore it."
        if not node_type:
            return

        self.node_types[node_path] = node_type

        submits = get_submits_from_flow_element(element)
        children = get_flow_children_from_flow_element(element)

        flow_data = {"flow_branch": flow_branch,
                     "flow_children_node_paths": children,
                     "flow_path": flow_path,
                     "module_name": get_module_name_for_element(element),
                     "module_path_inner": module_path,
                     "submits_children_node_paths": submits,
                     "type": node_type}

        if element.tag.lower() == NODE_TYPE.SWITCH:
            switch_type = element.attrib.get("type")
            if switch_type:
                flow_data["switch_type"] = switch_type

        self.flow_datas[node_path] = flow_data

        for child in children:
            self.flow_child_to_parent[child] = node_path

    def get_siblings(self, node_path):
        """
        returns a list of all node_path siblings, including this node_path
        """
        parent_node_path = self.get_parent(node_path)
        if not parent_node_path:
            return [node_path]
        parent = self.get_node_data(parent_node_path)
        return parent["flow_children_node_paths"]

    def get_parent(self, child_node_path):
        if child_node_path.endswith("/"):
            child_node_path = child_node_path[:-1]
        return self.flow_child_to_parent.get(child_node_path, "")

    def get_flow_branches(self):
        paths = [f["flow_branch"] for f in self.flow_datas.values()]
        return sorted(paths, key=len)

    def get_node_paths(self):
        return sorted(list(self.flow_datas.keys()), key=len)

    def get_flow_data(self, node_path):
        if node_path.endswith("/"):
            node_path = node_path[:-1]
        return self.flow_datas.get(node_path)

    def node_path_contains_switch(self, node_path):
        """
        Returns true if any nodes in this node_path are a switch.

        Starts with the root, then onward, so that the loop can be broken
        before get_node_data fails on switch paths.
        """
        chunks = [c for c in node_path.split("/") if c.strip()]
        segment = ""
        while chunks:
            segment += chunks[0]+"/"
            chunks = chunks[1:]
            if self.is_switch(segment):
                return True
        return False

    def is_switch(self, node_path):
        node_path = superstrip(node_path, "/ ")
        return self.node_types.get(node_path) == NODE_TYPE.SWITCH

    def is_npass_task(self, node_path):
        node_path = superstrip(node_path, "/ ")
        return self.node_types.get(node_path) == NODE_TYPE.NPASS_TASK

    def is_loop(self, node_path):
        node_path = superstrip(node_path, "/ ")
        return self.node_types.get(node_path) == NODE_TYPE.LOOP

    def get_children(self, node_path):
        assert type(node_path) is str
        node = self.get_node_data(node_path)
        return node["flow_children_node_paths"]

    def get_switch_index_from_datestamp(self, node_data, datestamp):
        "See get_switch_child_for_datestamp"
        assert type(node_data) is dict

        if not node_data["type"] == NODE_TYPE.SWITCH:
            return ""
        switch_type = node_data.get("switch_type")
        if switch_type == SWITCH_TYPE.HOUR:
            return datestamp[-2:]
        elif switch_type == SWITCH_TYPE.DAY_OF_WEEK:
            return str(get_day_of_week(datestamp))

        msg = pretty_kwargs(switch_type=switch_type, node_data=node_data)
        raise NotImplementedError(msg)

    def get_switch_child_for_datestamp(self, node_path, datestamp):
        """
        A switch can have different children, for example hour "00", or hour "12", or day of week is "2".
        This returns the node_path of the child for this datestamp.
        This code may seem like it belongs in datestamp "snapshot" logic, but here
        the flow for "00" is always the flow for "00", even if it's not "00".
        """

        node_data = self.get_node_data(node_path)
        switch_index = self.get_switch_index_from_datestamp(node_data, datestamp)

        if switch_index:
            child_path = node_path+"/"+switch_index
            if self.is_node_path(child_path):
                return child_path

        return ""

    def has_children(self, node_path):
        assert type(node_path) is str
        return bool(self.get_children(node_path))