from lxml import etree
from utilities import cache

"""
This class is a central place to open and parse all XML files, to avoid ever doing it twice.

The returned element should never be modified.
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
    
    @cache
    def get_elements_of_tag(self,element,tag):
        """
        Return a list of all elements in this element (including this element)
        with this tag, for example 'MODULE'
        """
        return element.xpath("//"+tag)
        
    @cache
    def get(self,xml_path,return_deepcopy=False):            
        return get_root_from_xml_path(xml_path,parser=self.parser)

xml_cache=XMLCache()