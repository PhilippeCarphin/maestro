from lxml import etree
import copy

"""
This class is a central place to open and parse all XML files, to avoid ever doing it twice.

The returned element should never be modified, unless return_deepcopy is used.
"""

class XMLCache():
    def __init__(self):
        self.xml_path_to_lxml_root={}
    
    def get(self,xml_path,return_deepcopy=False):
        if xml_path not in self.xml_path_to_lxml_root:
            try:
                tree=etree.parse(xml_path)
            except:
                return None
            
            root=tree.getroot()
            self.xml_path_to_lxml_root[xml_path]=root
        
        element=self.xml_path_to_lxml_root[xml_path]
        
        if return_deepcopy:
            element=copy.deepcopy(element)
            
        return element

xml_cache=XMLCache()