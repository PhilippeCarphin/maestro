
import unittest

from utilities import get_key_value_from_path, get_true_host
from constants import RESOURCES_HOME1, RESOURCES_HOME2, TURTLE_ME_PATH, DEFAULT_BATCH_RESOURCES
from maestro_experiment import MaestroExperiment

"""
Tests for finding and parsing resource DEF and XML files.
    overrides.def
    default_resources.def
    resources/resources.def
    
    resources/../turtleTask1.xml
"""

TURTLE_DATESTAMP1="2020040100"

class TestMaestroResources(unittest.TestCase):
    
    def test_get_resource_value(self):
        path=RESOURCES_HOME1+".suites/default_resources.def"
        result=get_key_value_from_path("FRONTEND",path)
        expected="frontend-def-res-home1"
        self.assertEqual(result,expected)
    
    def test_me_get_resource_value(self):
        me=MaestroExperiment(TURTLE_ME_PATH,user_home=RESOURCES_HOME1)
        
        "ignore default_resources.def because task resource xml exists"
        result=me.get_resource_value_from_key("FRONTEND")
        expected="turtle-frontend"
        self.assertEqual(result,expected)
        
        result=me.get_resource_value_from_key("SEQ_DEFAULT_MACHINE")
        expected="turtle-default-machine"
        self.assertEqual(result,expected)
    
        "ignore task resource xml because overrides.def exists"
        me=MaestroExperiment(TURTLE_ME_PATH,user_home=RESOURCES_HOME2)
        result=me.get_resource_value_from_key("FRONTEND")
        expected="overrides-home2-frontend"
        self.assertEqual(result,expected)
        
        result=me.get_resource_value_from_key("SEQ_DEFAULT_MACHINE")
        expected="overrides-home2-default-machine"
        self.assertEqual(result,expected)
    
    def test_me_node_data_resources(self):
        "values in node_data that are obtained from the XML files in 'resources' "
        
        "empty XML, default resources"
        path="/home/that/does/not/exist/"
        me=MaestroExperiment(TURTLE_ME_PATH,user_home=path)
        node_path="turtle/turtleTask2"
        result_node_data=me.get_node_data(node_path)        
        "defaults presently found in SeqNode.c around line 680"
        
        for key,expected in DEFAULT_BATCH_RESOURCES.items():
            self.assertIn(key,result_node_data)
            result=result_node_data[key]
            self.assertEqual(result,expected)
        
        "use resources file and xml file to figure out custom value"
        me=MaestroExperiment(TURTLE_ME_PATH,user_home=RESOURCES_HOME2)
        node_path="turtle/turtleTask1"
        result_node_data=me.get_node_data(node_path)
        machine="overrides-home2-default-machine"
        expected=machine
        result=result_node_data["machine"]
        self.assertEqual(result,expected)
        
        "correct machine is appended to log path"
        result=me.get_latest_success_log(node_path)
        self.assertTrue(result.endswith("@"+machine))
        
        
        
        
        
        
        
        
    
        