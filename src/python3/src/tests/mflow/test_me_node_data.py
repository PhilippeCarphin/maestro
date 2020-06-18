import unittest

from maestro.experiment import MaestroExperiment
from tests.path import BIG_ME_PATH, TURTLE_ME_PATH, SUBMIT_CHAIN_ME_PATH
from constants import JSON_SCHEMAS, NODE_TYPE
from utilities import assert_valid_json, pretty, get_true_host
from mflow.utilities.resources import insert_default_batch_data
from tests.cache import G1_MINI_ME, TURTLE_ME, BIG_ME, SUBMIT_CHAIN_ME

"""
Tests for getting information about nodes.
"""

TURTLE_DATESTAMP1="2020040100"

class TestMaestroExperimentNodeData(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=5000
        
    def test_default_machine(self):
        "machine is SEQ_DEFAULT_MACHINE from resources.def if undefined in <BATCH>"
        
        me=TURTLE_ME
        node_data=me.get_node_data("turtle/TurtlePower/BossaNova/donatello")
        result=node_data["machine"]
        expected="turtle-default-machine"
        self.assertEqual(expected,result)        
            
    def test_get_node_data_module(self):
        node_path="sample"
        me=BIG_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        
        children=["sample/Different_Hosts",
                  "sample/Dependencies",
                  "sample/MoreDependencies",
                  "sample/npasstest",
                  "sample/work_unit",
                  "sample/worker",
                  "sample/Loop_example",
                  "sample/switch_hour",
                  "sample/switchmod",
                  "sample/deploop",
                  "sample/depswitch",
                  "sample/submit_test"]
        expected={"catchup":4,
                  "flow_children_node_paths":children,
                  "config_path":BIG_ME_PATH+"modules/sample/container.cfg",
                  "loop_indexes_available":[],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/sample/flow.xml",
                  "machine":"complete-exp-default-machine",
                  "module_name":"sample",
                  "name":"sample",
                  "path":node_path,
                  "resource_path":BIG_ME_PATH+"resources/sample/container.xml",
                  "submits_children_node_paths":children,
                  "task_path":"",
                  "type":NODE_TYPE.MODULE}
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
        
    def test_get_node_g1_task(self):
        node_path="main/pre_assimcycle/cutoff/cutoff"        
        me=G1_MINI_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        
        expected={"catchup":4,
                  "flow_children_node_paths":[],
                  "config_path":me.path+"modules/cutoff/cutoff.cfg",
                  "loop_indexes_available":[],
                  "flow_branch":"main/pre_assimcycle/get_arcdata_cutoff/cutoff/submit_families/cutoff",
                  "flow_path":me.path+"modules/cutoff/flow.xml",
                  "machine":"g1-mini-default-machine",
                  "module_name":"cutoff",
                  "name":"cutoff",
                  "path":node_path,
                  "resource_path":me.path+"resources/main/pre_assimcycle/cutoff/cutoff.xml",
                  "submits_children_node_paths":[],
                  "task_path":me.path+"modules/cutoff/cutoff.tsk",
                  "type":NODE_TYPE.NPASS_TASK}
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
    
    def test_get_node_datatask_with_child(self):
        node_path="turtle/turtleTask1"        
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        
        children=["turtle/turtleTask2"]
        expected={"catchup":60,
                  "cpu":2,
                  "flow_children_node_paths":children,
                  "config_path":TURTLE_ME_PATH+"modules/turtle/turtleTask1.cfg",
                  "loop_indexes_available":[],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/turtle/flow.xml",
                  "machine":"turtle-default-machine",
                  "memory":"4G",
                  "module_name":"turtle",
                  "name":"turtleTask1",
                  "path":node_path,
                  "queue":"production",
                  "resource_path":TURTLE_ME_PATH+"resources/turtle/turtleTask1.xml",
                  "submits_children_node_paths":children,
                  "task_path":TURTLE_ME_PATH+"modules/turtle/turtleTask1.tsk",
                  "type":NODE_TYPE.TASK,
                  "wallclock":60} 
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
    
    def test_get_node_datatask_under_loop(self):
        node_path="turtle/TurtlePower/shredderTask"        
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)

        expected={"catchup":4,
                  "flow_children_node_paths":[],
                  "config_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/shredderTask.cfg",
                  "loop_indexes_available":[],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/turtle/flow.xml",
                  "machine":"turtle-default-machine",
                  "module_name":"turtle",
                  "name":"shredderTask",
                  "path":node_path,
                  "resource_path":TURTLE_ME_PATH+"resources/turtle/TurtlePower/shredderTask.xml",
                  "submits_children_node_paths":[],
                  "task_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/shredderTask.tsk",
                  "type":NODE_TYPE.TASK}       
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
        
    def test_get_node_datatask_under_loops(self):
        node_path="turtle/TurtlePower/BossaNova/donatello"        
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)

        expected={"catchup":4,
                  "flow_children_node_paths":[],
                  "config_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/BossaNova/donatello.cfg",
                  "loop_indexes_available":[],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/turtle/flow.xml",
                  "machine":"turtle-default-machine",
                  "module_name":"turtle",
                  "name":"donatello",
                  "path":node_path,
                  "resource_path":TURTLE_ME_PATH+"resources/turtle/TurtlePower/BossaNova/donatello.xml",
                  "submits_children_node_paths":[],
                  "task_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/BossaNova/donatello.tsk",
                  "type":NODE_TYPE.TASK}        
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
        
    def test_get_node_datatask_catchup(self):
        node_path="turtle/turtleSlowpoke"        
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        self.assertEqual(result["catchup"],9)

    def test_get_node_dataloop1(self):
        node_path="turtle/TurtlePower"        
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        
        children=["turtle/TurtlePower/shredderTask",
                  "turtle/TurtlePower/splinterTask",
                  "turtle/TurtlePower/BossaNova",
                  "turtle/TurtlePower/pizza1"]
        expected={"catchup":4,
                  "flow_children_node_paths":children,
                  "config_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/container.cfg",
                  "loop_indexes_available":[0,1],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/turtle/flow.xml",
                  "machine":"turtle-default-machine",
                  "module_name":"turtle",
                  "name":"TurtlePower",
                  "path":node_path,
                  "resource_path":TURTLE_ME_PATH+"resources/turtle/TurtlePower/container.xml",
                  "submits_children_node_paths":children,
                  "task_path":"",
                  "type":NODE_TYPE.LOOP}        
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
        
    def test_get_node_dataloop2(self):
        node_path="turtle/TurtlePower/BossaNova"
        me=TURTLE_ME
        result=me.get_node_data(node_path)
        assert_valid_json(result,JSON_SCHEMAS.NODE)
        
        children=["turtle/TurtlePower/BossaNova/donatello"]
        expected={"catchup":4,
                  "flow_children_node_paths":children,
                  "config_path":TURTLE_ME_PATH+"modules/turtle/TurtlePower/BossaNova/container.cfg",
                  "loop_indexes_available":[0,3,6,9],
                  "flow_branch":node_path,
                  "flow_path":me.path+"modules/turtle/flow.xml",
                  "machine":"turtle-default-machine",
                  "module_name":"turtle",
                  "name":"BossaNova",
                  "path":node_path,
                  "resource_path":TURTLE_ME_PATH+"resources/turtle/TurtlePower/BossaNova/container.xml",
                  "submits_children_node_paths":children,
                  "task_path":"",
                  "type":NODE_TYPE.LOOP}
        insert_default_batch_data(expected)
        
        msg=pretty_objects(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)
        
    def test_submit_chain(self):
        """
        In gdps, the gem module flow.xml has a chain of submit elements at the same XML tree level.
        This tests a similar flow.
        """
        
        flow_branches=["module1",
                    "module1/task1",
                    "module1/task1/task2",
                    "module1/task1/task2/task3",
                    "module1/task1/task2/task3/task4",
                    "module1/task1/task2/task3/task4/task5"]        
        node_paths=["module1",
                    "module1/task1",
                    "module1/task2",
                    "module1/task3",
                    "module1/task4",
                    "module1/task5"]   
        me=SUBMIT_CHAIN_ME
        
        results=me.get_flow_branches()
        for flow_branch in flow_branches:
            self.assertIn(flow_branch,flow_branches)
        self.assertEqual(flow_branches,results)
        
        results=me.get_node_paths()
        for node_path in node_paths:
            self.assertIn(node_path,node_paths)        
        self.assertEqual(node_paths,results)
        
def pretty_objects(**kwargs):
    "return a string of this dict showing keys and pretty printed objects"
    lines=[]
    stars="*"*40
    for key,item in kwargs.items():
        lines.append("\n\n"+stars)
        lines.append("   %s"%key.upper())
        lines.append(stars)
        lines.append(pretty(item))
    return "\n".join(lines)
        