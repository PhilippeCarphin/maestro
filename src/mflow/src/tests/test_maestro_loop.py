
import unittest
from lxml import etree

from constants import TURTLE_ME_PATH, NODE_STATUS
from maestro_experiment import MaestroExperiment
from maestro.loop import get_loop_indexes_from_loop_data, get_loop_composite_data_from_xml, get_loop_indexes_from_expression
from tests.cache import G0_MINI_ME, TURTLE_ME

"""
Tests for getting information about nodes.
"""

TURTLE_DATESTAMP1="2020040100"

class TestMaestroLoop(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=2000
        
    def test_default_loop_values(self):
        """
        In geps/g2 node_path:
            main/geps_mod/enkf_mod/Trials/gem_loop
        there is no "step" so we assume it is 1.
        """
        path=TURTLE_ME_PATH+"resources/turtle/TurtlePower/container.xml"
        xml=TURTLE_ME.get_resource_xml(path)
        result=get_loop_composite_data_from_xml(xml)
        expected=[{"start":0,"set":1,"end":1,"step":1}]
        self.assertEqual(result,expected)
        
    def test_npt_indexes(self):
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=TURTLE_DATESTAMP1)
        
        node_path="turtle/TurtlePower/pizza1"
        expected={"TurtlePower":0}
        result=me.get_first_index_selection(node_path)
        self.assertEqual(expected,result)
        
        node_path="turtle/TurtlePower/pizza2"
        result=me.get_index_map(node_path)
        expected={"TurtlePower":[0,1],
                  "pizza2":["p2index1","p2index2"]}
        self.assertEqual(expected,result,msg="\n\n"+str(result))
        
        expected={"TurtlePower":0,"pizza2":"p2index1"}
        result=me.get_first_index_selection(node_path)
        self.assertEqual(expected,result)
        
        node_path="turtle/TurtlePower/pizza3"
        result=me.get_index_map(node_path)
        expected={"TurtlePower":[0,1],
                  "pizza3":["p3index1","p3index2"]}
        self.assertEqual(expected,result,msg="\n\n"+str(result))
        
        expected={"TurtlePower":0,"pizza3":"p3index1"}
        result=me.get_first_index_selection(node_path)
        self.assertEqual(expected,result)
        
    def test_loop_expression(self):
        "one"
        expression="0:3:1:1"
        result=get_loop_indexes_from_expression(expression)
        expected=[0,1,2,3]
        self.assertEqual(result,expected)
        
        "two"
        expression="0:3:1:1,5:10:2:1"
        result=get_loop_indexes_from_expression(expression)
        expected=[0,1,2,3,5,7,9]
        self.assertEqual(result,expected)
        
        "first broken"
        expression="0:3:1,5:10:2:1"
        result=get_loop_indexes_from_expression(expression)
        expected=[5,7,9]
        self.assertEqual(result,expected)
        
        "both broken"
        expression="0:3:1,5:a:2:1"
        result=get_loop_indexes_from_expression(expression)
        expected=[]
        self.assertEqual(result,expected)
    
    def test_get_loop_indexes_from_experiment(self):
        node_path="main/assimcycle/forecast/loop_post_gem"
        node_data=G0_MINI_ME.get_node_data(node_path)
        result=node_data["loop_indexes_available"]
        expected=[i for i in range(0,673,24)]
        self.assertEqual(result,expected)
        
    def test_get_first_loop_index_selection(self):
        node_paths=["turtle/TurtlePower/BossaNova",
                    "turtle/TurtlePower/BossaNova/donatello"]
        expected={"TurtlePower":0,"BossaNova":0}
        me=TURTLE_ME
        for node_path in node_paths:
            result=me.get_first_index_selection(node_path)
            self.assertEqual(expected,result)
        
    def test_get_node_status_task_loop_end(self):
        node_path="turtle/TurtlePower/BossaNova/donatello"
        loop_index_selection={"TurtlePower":1,"BossaNova":3}
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=TURTLE_DATESTAMP1)
        result=me.get_node_status(node_path,loop_index_selection=loop_index_selection)
        self.assertEqual(NODE_STATUS.END,result)
        
        result=me.get_node_status(node_path,loop_index_selection=loop_index_selection)
        self.assertEqual(NODE_STATUS.END,result)
        
    def test_get_loop_index_map(self):
        node_path="turtle/TurtlePower/BossaNova/donatello"
        me=TURTLE_ME
        result=me.get_index_map(node_path)
        expected={"TurtlePower":[0,1],"BossaNova":[0,3,6,9]}
        self.assertEqual(result,expected)
        
    def test_get_loop_indexes(self):
        result=get_loop_indexes_from_loop_data(0,10,2)
        expected=[0,2,4,6,8,10]
        self.assertEqual(result,expected)
        
        result=get_loop_indexes_from_loop_data(10,0,3)
        expected=[]
        self.assertEqual(result,expected)
        
    def test_get_loop_composite_data(self):
        node_path="turtle/TurtlePower/BossaNova"
        me=TURTLE_ME
        expected=[{"start":0,"set":2,"end":10,"step":3}]        
        result=me.get_loop_composite_data(node_path)
        self.assertEqual(result,expected)        
            