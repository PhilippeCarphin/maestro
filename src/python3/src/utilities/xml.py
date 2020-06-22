from lxml import etree
import copy

"""
This class is a central place to open and parse all XML files, to avoid ever doing it twice.

The returned element should never be modified, unless return_deepcopy is used.
"""

def is_valid_xml(path):
    """
    Returns true if an XML at this path can be parsed as XML.
    """
    return get_root_from_xml_path(path) is not None

def get_root_from_xml_path(path,parser=None):
    if not parser:
        parser=etree.XMLParser(remove_comments=True)
        
    try:
        tree=etree.parse(path,parser=parser)
    except:
        return None
    
    return tree.getroot()

class XMLCache():
    def __init__(self):
        self.parser=etree.XMLParser(remove_comments=True)
        self.xml_path_to_lxml_root={}
    
    def get(self,xml_path,return_deepcopy=False):
        if xml_path not in self.xml_path_to_lxml_root:            
            root=get_root_from_xml_path(xml_path,parser=self.parser)
            if root is None:
                return
            self.xml_path_to_lxml_root[xml_path]=root
        
        element=self.xml_path_to_lxml_root[xml_path]
        
        if return_deepcopy:
            element=copy.deepcopy(element)
            
        return element

xml_cache=XMLCache()