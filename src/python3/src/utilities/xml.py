from lxml import etree
from utilities import cache

"""
This class is a central place to open and parse all XML files, to avoid ever doing it twice.

The returned element should never be modified.
"""


class XMLCache():
    def __init__(self):
        self.parser=etree.XMLParser(remove_comments=True)
    
    @cache
    def is_valid_xml(self,path):
        """
        Returns true if an XML at this path can be parsed as XML.
        """
        return self.get_root_from_xml_path(path) is not None
    
    @cache
    def get_root_from_xml_path(self,path):
            
        try:
            tree=etree.parse(path,parser=self.parser)
        except:
            return None
        
        return tree.getroot()
    
    @cache
    def get_elements_of_tag(self,element,tag):
        """
        Return a list of all elements in this element (including this element)
        with this tag, for example 'MODULE'
        """
        return element.xpath("//"+tag)
        
    @cache
    def get(self,xml_path):            
        return self.get_root_from_xml_path(xml_path)

xml_cache=XMLCache()