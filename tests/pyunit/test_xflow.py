import unittest
from utilities import *

class TestXFlow(unittest.TestCase):
	        
    def test_basic_usage(self):
        cmd=SSM_USE_COMMAND + "xflow -exp "+PATH.SAMPLE_EXP1
        output,status = get_output(cmd, use_popen = True)
        
        self.assertIn("xflow_displayFlow()",output)
        self.assertNotIn("XML Document Not Found", output)
        self.assertNotIn("NODE", output)
        self.assertNotIn("-l argument requires -n ar gument!", output)
