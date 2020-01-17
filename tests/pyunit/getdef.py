import unittest
from utilities.utils import *
from os.path import expanduser

class TestGetDef(unittest.TestCase):
    def test_basic_getdef(self):
        cmd="getdef -e /home/smco500/.suites/rdps/r1 resources FRONTEND"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
