import unittest
from utilities import *

class TestScanExp(unittest.TestCase):
	
    def test_basic_usage(self):
        cmd=SSM_USE_COMMAND+success_commands["scanexp"]
        output,status = get_output(cmd)
        expected="""<SUBMITS sub_name="current_index_dep"/>"""
        self.assertIn(expected, output)
