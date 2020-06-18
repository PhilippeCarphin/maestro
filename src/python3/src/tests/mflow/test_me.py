import unittest

from maestro.experiment import MaestroExperiment
from constants import BIG_ME_PATH, TURTLE_ME_PATH, JSON_SCHEMAS, NODE_TYPE, RESOURCES_HOME3
from utilities import assert_valid_json, pretty

"""
Tests for the MaestroExperiment class.
"""

class TestMaestroExperiment(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=5000
        
    def test_deep_path(self):
        """
        paths like:
            $SEQ_EXP_HOME/listings/folder1/folder2
        should still open that experiment just fine.
        """
        me=MaestroExperiment(BIG_ME_PATH+"/resources/sample")
        self.assertEqual(me.path,BIG_ME_PATH)
        
        "even when inside no longer existing folders"
        me=MaestroExperiment(BIG_ME_PATH+"/does/not-exist/123")
        self.assertEqual(me.path,BIG_ME_PATH)
        
    def test_get_workdir_path(self):
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,
                             datestamp=datestamp,
                             user_home=RESOURCES_HOME3)
        node_path="turtle/turtleTask1"
        result=me.get_workdir_path(node_path)
        expected=TURTLE_ME_PATH+"hub/eccc-ppp3/work/%s0000/turtle/turtleTask1/"%datestamp
        self.assertEqual(result,expected)
        
    def test_switch_child(self):        
        me=MaestroExperiment(BIG_ME_PATH)
        node_path="sample/switch_hour"
        
        result=me.get_switch_child_for_datestamp(node_path,"2020040100")
        expected="sample/switch_hour/00"
        self.assertTrue(me.is_node_path(expected))
        self.assertEqual(result,expected)
        
        result=me.get_switch_child_for_datestamp(node_path,"2020040112")
        expected="sample/switch_hour/12"
        self.assertTrue(me.is_node_path(expected))
        self.assertEqual(result,expected)
        
        "thursday" 
        node_path="sample/switchmod/switch_dow"
        result=me.get_switch_child_for_datestamp(node_path,"2020051200")
        expected="sample/switchmod/switch_dow/2"
        self.assertTrue(me.is_node_path(expected))
        self.assertEqual(result,expected)
            
    def test_complete_experiment_nodes(self):
        me=MaestroExperiment(BIG_ME_PATH)
        assert_valid_json(me.root_node_data,JSON_SCHEMAS.NODE)
        self.assertEqual(me.root_node_data["name"],"sample",msg=pretty(me.root_node_data))
        
    def test_tree_traversal(self):
        me=MaestroExperiment(TURTLE_ME_PATH)
        
        result=me.get_siblings("turtle")
        expected=["turtle"]
        self.assertEqual(result,expected)
        
        result=me.get_siblings("turtle/TurtlePower")
        expected=["turtle/turtleTask1",
                  "turtle/TurtlePower",
                  "turtle/turtleSlowpoke",
                  "turtle/turtleMemory"]
        self.assertEqual(result,expected)
        
        result=me.get_siblings("turtle/TurtlePower/splinterTask")
        expected=["turtle/TurtlePower/shredderTask",
                  "turtle/TurtlePower/splinterTask",
                  "turtle/TurtlePower/BossaNova",
                  "turtle/TurtlePower/pizza1"]
        self.assertEqual(result,expected)
        
        result=me.get_parent("turtle/TurtlePower/splinterTask")
        expected="turtle/TurtlePower"
        self.assertEqual(result,expected)
        
        result=me.get_parent("turtle/turtleTask2")
        expected="turtle/turtleTask1"
        self.assertEqual(result,expected)        
        
    def test_node_paths(self):
        me=MaestroExperiment(BIG_ME_PATH)
        """
        No node_path should end in a slash, for consistency, even though this ambiguity is 
        allowed in maestro arguments.
        """
        slashes=[node_path for node_path in me.flow_datas if node_path.endswith("/")]
        self.assertFalse(slashes)
        
    def test_children(self):
        me=MaestroExperiment(TURTLE_ME_PATH)
        
        node="turtle/TurtlePower"
        self.assertTrue(me.has_children(node))
        children=me.get_children(node)
        expected=["turtle/TurtlePower/shredderTask",
                  "turtle/TurtlePower/splinterTask",
                  "turtle/TurtlePower/BossaNova",
                  "turtle/TurtlePower/pizza1"]
        self.assertEqual(children,expected)
        
        node="turtle/turtleMemory"
        self.assertFalse(me.has_children(node))
        children=me.get_children(node)
        self.assertEqual(children,[])
    
    def test_has_indexes(self):
        me=MaestroExperiment(TURTLE_ME_PATH)
        
        node="turtle/TurtlePower"
        self.assertTrue(me.has_indexes(node))
        
        node="turtle/TurtlePower/BossaNova"
        self.assertTrue(me.has_indexes(node))
        
        node="turtle"
        self.assertFalse(me.has_indexes(node))
        
        node="turtle/TurtlePower/shredderTask"
        self.assertFalse(me.has_indexes(node))
        
    def test_module(self):
        me=MaestroExperiment(BIG_ME_PATH)
        node_path="sample/Different_Hosts/IBMTask"
        node_data=me.get_node_data(node_path)
        self.assertEqual(node_data["type"],NODE_TYPE.TASK)
        