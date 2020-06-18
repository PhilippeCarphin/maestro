import unittest

from mflow.tui.text_flow import TextFlow
from maestro.experiment import MaestroExperiment
from tests.path import TURTLE_ME_PATH
from utilities import pretty_kwargs
from tests.utilities import get_test_config
from tests.cache import G1_MINI_ME, BIG_ME, TURTLE_ME

"""
Tests for the MaestroExperiment class.
"""

TURTLE_FLOW_NORMAL="""
 turtle |----->  turtleTask1  ----->  turtleTask2
        |
        |
        |----->  TurtlePower |----->  shredderTask
        |                    |
        |                    |
        |                    |----->  splinterTask
        |                    |
        |                    |
        |                    |----->  BossaNova  ----->  donatello
        |                    |
        |                    |
        |                    |----->  pizza1  ----->  pizza2  ----->  pizza3
        |
        |
        |----->  turtleSlowpoke
        |
        |
        |----->  turtleMemory"""

class TestTextFlow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=5000
        
    def test_node_margin_bottom(self):
        lines_without_empty=[line for line in TURTLE_FLOW_NORMAL.split("\n") if len(set(line))>2]
        expected="\n"+"\n".join(lines_without_empty)
        
        tui_config=get_test_config(NODE_MARGIN_BOTTOM=0)
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tf=TextFlow(me,tui_config=tui_config)        
        result=tf.get_string_flow()
        
        msg=pretty_kwargs(result=result,expected=expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_loop_indexes(self):
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tf=TextFlow(me)
        
        node_path="turtle/TurtlePower"
        result=tf.get_selected_index_for_node(node_path)
        self.assertEqual(result,0)
        
        tf.set_node_selected_loop_index(node_path,1)
        result=tf.get_selected_index_for_node(node_path)
        self.assertEqual(result,1)
        
        node_path="turtle/TurtlePower/BossaNova"
        tf.set_node_selected_loop_index(node_path,3)
        result=tf.get_loop_index_selection(node_path)
        expected={"TurtlePower":1,"BossaNova":3}
        self.assertEqual(result,expected)
        
        node_path="turtle/TurtlePower/BossaNova/donatello"
        result=tf.get_loop_index_selection(node_path)
        self.assertEqual(result,expected)
        
    def test_get_node_path_from_xy(self):
        "nodes with height 1, no extra info"
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tf=TextFlow(me)
        
        coords={(3,1):"turtle",
                (19,1):"turtle/turtleTask1",
                (1,2):"",
                (21,4):"turtle/TurtlePower",
                (61,10):"turtle/TurtlePower/BossaNova/donatello",
                (-5,0):"",
                (50000,0):""}
        
        for xy,expected in coords.items():
            x,y=xy
            result=tf.get_node_path_from_xy(x,y)
            msg="(%s,%s) '%s'"%(x,y,expected)
            self.assertEqual(result,expected,msg=msg)
            
    def test_get_node_path_from_xy_tall(self):
        "nodes with height 2"
        datestamp="2020040100"
        tui_config=get_test_config(FLOW_NODE_SHOW_TYPE=True)
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tf=TextFlow(me,tui_config=tui_config)
        
        coords={(3,1):"turtle",
                (3,2):"turtle",
                (3,3):"",
                (19,1):"turtle/turtleTask1",
                (21,4):"",
                (21,5):"turtle/TurtlePower",
                (21,6):"turtle/TurtlePower",
                (21,7):"",
                (61,13):"turtle/TurtlePower/BossaNova/donatello",
                (-5,0):"",
                (50000,0):""}
        
        for xy,expected in coords.items():
            x,y=xy
            result=tf.get_node_path_from_xy(x,y)
            msg="xy = (%s,%s) node = '%s'"%(x,y,expected)
            self.assertEqual(result,expected,msg=msg)
            
    def test_hour_switch(self):
        "some switches only show their branches for certain times/hours/days"
        
        test_cases=(("2020040100","|----->  depswitch = 00  ----->  intraloopDependencies |----->  dependee"),
               ("2020040112","|----->  depswitch = 12  ----->  t2"),
               ("2020040107","|----->  depswitch = 07"),)
        
        me=BIG_ME
        for datestamp,expected in test_cases:
            me.set_snapshot(datestamp)
            tf=TextFlow(me)
            text=tf.get_string_flow()
            lines=text.split("\n")
            lines=[line.strip() for line in lines if "depswitch" in line]
            self.assertEqual(len(lines),1)
            depswitch_line=lines[0]        
            self.assertEqual(depswitch_line,expected)

    def test_module_flow(self):
        "test that different flow XMLs are found in modules"
        datestamp="2020040100"
        me=BIG_ME
        me.set_snapshot(datestamp)
        tf=TextFlow(me)
        expected="\n sample |----->  Different_Hosts |----->  IBMTask"       
        result=tf.get_string_flow()[:500]
        msg="\n\nresult:\n"+result
        self.assertTrue(result.startswith(expected),msg=msg)
            
    def test_g1_first_line(self):
        "the first text line of the g1 flow"
        datestamp="2020040100"
        me=G1_MINI_ME
        me.set_snapshot(datestamp)
        tf=TextFlow(me)
        expected="\n main |----->  pre_assimcycle |----->  get_arcdata_cutoff  ----->  cutoff  ----->  submit_families  ----->  cutoff"
        result=tf.get_string_flow()[:800]
        msg=pretty_kwargs(result=result,expected_first_line=expected)
        self.assertTrue(result.startswith(expected),msg=msg)
        
    def test_turtle_collapse_node(self):
        datestamp="2020040100"
        me=TURTLE_ME
        me.set_snapshot(datestamp)
        tf=TextFlow(me)
        expected="""
 turtle |----->  turtleTask1  ----->  turtleTask2
        |
        |
        |----->  TurtlePower
        |        (collapsed)
        |
        |
        |----->  turtleSlowpoke
        |
        |
        |----->  turtleMemory"""
       
        tf.set_node_collapsed("turtle/TurtlePower",True)       
        result=tf.get_string_flow()
        msg="\n\nresult:\n"+result
        self.assertEqual(result,expected,msg=msg)
        
        tf.set_node_collapsed("turtle/TurtlePower",False)       
        expected=TURTLE_FLOW_NORMAL
        result=tf.get_string_flow()
        msg="\n\nresult:\n"+result
        self.assertEqual(result,expected,msg=msg)
            
    def test_turtle_flow(self):
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tf=TextFlow(me)
        expected=TURTLE_FLOW_NORMAL       
        result=tf.get_string_flow()
        msg="\n\nresult:\n"+result
        self.assertEqual(result,expected,msg=msg)
        
    def test_turtle_flow_node_type(self):
        datestamp="2020040100"
        me=MaestroExperiment(TURTLE_ME_PATH,datestamp=datestamp)
        tui_config=get_test_config(FLOW_NODE_SHOW_TYPE=True)
        tf=TextFlow(me,tui_config=tui_config)
        expected="""
 turtle   |----->  turtleTask1  ----->  turtleTask2
 (module) |        (task)               (task)
          |
          |
          |----->  TurtlePower |----->  shredderTask
          |        (loop)      |        (task)
          |                    |
          |                    |
          |                    |----->  splinterTask
          |                    |        (task)
          |                    |
          |                    |
          |                    |----->  BossaNova  ----->  donatello
          |                    |        (loop)             (task)
          |                    |
          |                    |
          |                    |----->  pizza1  ----->  pizza2        ----->  pizza3
          |                             (task)          (npass_task)          (npass_task)
          |
          |
          |----->  turtleSlowpoke
          |        (task)
          |
          |
          |----->  turtleMemory
                   (task)"""
       
        result=tf.get_string_flow()
        msg="\n\nresult:\n"+result
        self.assertEqual(result,expected,msg=msg)