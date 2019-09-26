import unittest
from utilities import *

class TestXFlowOverview(unittest.TestCase):
		
    def test_basic_usage(self):
        cmd=SSM_USE_COMMAND + "xflow_overview -exp "+PATH.SAMPLE_EXP1
        output,status = get_output(cmd, use_popen = True)
        
        expected="starting xflow_overview with exp"
        self.assertIn(expected,output)
        
        self.assertNotIn("SEQ_EXP_HOME", output)
        self.assertNotIn("ERROR", output)
        self.assertNotIn("bad switch", output)
        self.assertNotIn("couldn't connect to display", output)
