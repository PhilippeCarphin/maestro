import unittest

from maestro_experiment import MaestroExperiment
from tests.path import TURTLE_ME_PATH, RESOURCES_HOME3

"""
Tests for the TestMaestroExperiment class.
"""

class TestMaestroExperimentLogs(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=5000
        
    def test_get_listings(self):
        datestamp="2020032200"
        me=MaestroExperiment(TURTLE_ME_PATH,
                             datestamp=datestamp,
                             user_home=RESOURCES_HOME3)
        folder=TURTLE_ME_PATH+"listings/latest/"
        host="eccc-ppp3"
        
        expected=folder+"turtle.20200322000000.submission@"+host
        result=me.get_latest_submission_log("turtle")
        self.assertEqual(result,expected)
        
        node="turtle/TurtlePower/BossaNova/donatello"
        expected=folder+node+".+0+0.20200322000000.success@"+host
        result=me.get_latest_success_log(node)
        self.assertEqual(result,expected)
        
        node="turtle/TurtlePower/BossaNova/donatello"
        expected=folder+node+".+1+3.20200322000000.success@"+host
        indexes={"TurtlePower":1,"BossaNova":3}
        result=me.get_latest_success_log(node,loop_indexes_selected=indexes)
        self.assertEqual(result,expected)
        
        node="turtle/TurtlePower/BossaNova/donatello"
        expected=folder+node+".+1+0.20200322000000.success@"+host
        indexes={"TurtlePower":1}
        result=me.get_latest_success_log(node,loop_indexes_selected=indexes)
        self.assertEqual(result,expected)