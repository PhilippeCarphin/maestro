
"""
This code handles parsing and variable substitutions in resource XML files.

This abstract class is not meant to be instantiated, only inherited.
"""

from lxml import etree
import os.path

from utilities import get_key_value_from_path, superstrip
from home_logger import logger
from constants import DEFAULT_BATCH_RESOURCES

class ME_Resources():    

    def get_resource_xml(self,path):
        """
        Parses the XML at path, and returns the lxml element where
        variables like ${FRONTEND} has been replaced with their resource variable value.
        """
        if path not in self.resource_xml_cache:                    
            if not os.path.isfile(path):
                return None
            
            try:
                tree=etree.parse(path, parser=etree.XMLParser(remove_comments=True))
            except etree.XMLSyntaxError:
                logger.error("lxml failed to parse resource XML: '%s'"%path)
                return None
            root=tree.getroot()
            
            self.insert_resources_into_xml(root)
            
            self.resource_xml_cache[path]=root
            
        return self.resource_xml_cache[path]

    def insert_resources_into_xml(self,root):
        """
        Replace all attributes in this xml element with resource variable values, like:
            machine='${MACHINE}'
        with:
            machine='eccc-ppp4'
        """
        
        for element in root.iter():
            for key in element.attrib:
                value=element.attrib[key]
                if value.startswith("$"):
                    name=superstrip(value,"${}")
                    new_value=self.get_resource_value_from_key(name)
                    if new_value:
                        element.attrib[key]=new_value
        return root

    def get_batch_data_from_xml(self,path):
        """
        Given a resources XML path, returns a batch resource dictionary
        with keys like 'cpu' and 'wallclock'.
        """
        
        root=self.get_resource_xml(path)
        
        if root is None:
            return {}
                
        batch_elements=root.xpath("//BATCH")
        if len(batch_elements)==0:
            logger.debug("did not find <BATCH> in resource XML: '%s'"%path)
            return {}
        
        batch=batch_elements[0]
        result={}
        for key in DEFAULT_BATCH_RESOURCES:
            if key in batch.attrib:
                result[key]=batch.attrib[key]
        return result
    
    def get_resource_value_from_key(self,key):
        """
        Like getdef in SeqUtil.c SeqUtil_getdef.
        Search overrides.def, then resources/resources.def,
        the default_resources.def for the value of this key.
        """
        
        if key in self.resource_cache:
            return self.resource_cache[key]
        
        "starting with highest priority"
        paths=[self.user_home+".suites/overrides.def",
               self.path+"resources/resources.def",
               self.user_home+".suites/default_resources.def"]
        for path in paths:
            value=get_key_value_from_path(key,path)
            if value:
                return value
            
        "did not find variable anywhere"
        value=""
        
        self.resource_cache[key]=value
        
        return value
    