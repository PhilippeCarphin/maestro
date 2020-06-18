import unittest

from maestro.experiment import MaestroExperiment
from tests.path import TURTLE_ME_PATH, TURTLE_DATESTAMP1
from constants import NODE_STATUS
from tests.cache import GV_MINI_ME, TURTLE_ME

"""
Tests for getting information about nodes.
"""

class TestNodeStatus(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=2000
        
    def test_ord_soumet_abort(self):
        """
        there is no abort file in 'status' folder but it's still an abort,
        received from ord_soumet as a message, in logs folder
        """
        
        datestamp1="2020052700"
        datestamp2="2020052800"
        node_path="gdps_verif/SCORES_VS_OBSERVATIONS/Foreign_scores/Gfs_scores"
        
        "abort"
        me=GV_MINI_ME
        me.set_snapshot(datestamp1)
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.SUBMIT_FAILURE,result)
        
        "abort, then later end, is end"
        me=GV_MINI_ME
        me.set_snapshot(datestamp2)
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.END,result)
                
    def test_get_node_status_task_end(self):
        node_path="turtle/turtleTask1"
        me=TURTLE_ME
        me.set_snapshot(TURTLE_DATESTAMP1)
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.END,result)
        
    def test_get_node_status_task_abort(self):
        node_path="turtle/turtleMemory"
        me=TURTLE_ME
        me.set_snapshot(TURTLE_DATESTAMP1)
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.ABORT,result)
        
        node_path="turtle"
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.ABORT,result)
        
    def test_get_node_status_task_catchup(self):
        node_path="turtle/turtleSlowpoke"
        me=TURTLE_ME
        me.set_snapshot(TURTLE_DATESTAMP1)
        result=me.get_node_status(node_path)
        self.assertEqual(NODE_STATUS.CATCHUP,result)
