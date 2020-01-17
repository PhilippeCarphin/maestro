import unittest
from utilities.utils import *
from os.path import expanduser

class TestNodeInfo(unittest.TestCase):
    def test_basic_nodeinfo(self):
        cmd="nodeinfo -n /sample/Dependencies/downone/downtwo/dep_container_keyword -f type -e /home/dor001/.suites/sample_1.4.0 -v"
        output,status = get_output(SSM_USE_COMMAND + cmd)
        self.assertEqual(status,0)
