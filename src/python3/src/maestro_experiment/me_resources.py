
"""
This code handles parsing and variable substitutions in resource XML files.

This abstract class is not meant to be instantiated, only inherited.
"""

import re
from lxml import etree
import os.path

from utilities import get_key_value_from_path, superstrip
from home_logger import logger
from constants import DEFAULT_BATCH_RESOURCES

"""
Matches variables in curly brackets.
group0 is ${ABC}
group1 is ABC
"""      
CURLY_VARIABLE_REGEX=re.compile(r"\${([a-zA-Z0-9_]+)}")

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
            
            undefined=self.insert_resources_into_xml(root)
            if undefined:
                self.undefined_resource_variables[path]=undefined
            
            self.resource_xml_cache[path]=root
            
        return self.resource_xml_cache[path]
    
    def interpret_variables(self,text):
        """
        Given a string like:
            ${ABC}x${ABC}
        and ABC is defined in the resources as:
            123
        Returns a tuple:
            (text,undefined)
        where text is:
            123x123

        and undefined are any variables that were used but don't seem to be defined.
        """
        undefined=[]
        
        for match in CURLY_VARIABLE_REGEX.finditer(text):
            name=match.group(1)
            value=self.get_resource_value_from_key(name)                    
            if value:
                text.replace(match.group(0),value)
            else:
                undefined.append(name)
        
        return text,undefined        

    def insert_resources_into_xml(self,root):
        """
        Replace all attributes in this xml element with resource variable values, like:
            machine='${MACHINE}'
        with:
            machine='eccc-ppp4'
            
        Returns a list of variables that were used but don't seem to be 
        defined in the project.
        """
        
        undefined=[]
        
        for element in root.iter():
            for key in element.attrib:                
                a=element.attrib[key]
                element.attrib[key],b=self.interpret_variables(a)
                undefined+=b
                        
        return undefined
    
    def get_interpreted_resource_lxml_element(self,path):
        """
        everything, including loops, should use this to grab the etree
        instead of interpreting piecemeal
        
        all attributes should be interpreted the same way
        """
        assert 0

    def get_batch_data_from_xml(self,path):
        """
        Given a resources XML path, returns a batch resource dictionary
        with keys like 'cpu' and 'wallclock'.
        """
        self.get_interpreted_resource_lxml_element(path)
        root=self.get_resource_xml(path)
        
        if root is None:
            return {}
                
        batch_elements=root.xpath("//BATCH")
        if len(batch_elements)==0:
            logger.debug("did not find <BATCH> in resource XML: '%s'"%path)
            return {}
        
        batch=batch_elements[0]
        result={}
        keys=list(DEFAULT_BATCH_RESOURCES.keys())+["machine"]
        for key in keys:
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
    