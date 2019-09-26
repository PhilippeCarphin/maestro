import unittest
from utilities import *

class TestMServer(unittest.TestCase):

    def test_basic_usage(self):
        cmd=success_commands["madmin"]
        output,status = get_output(cmd)
        self.assertIn("Server is Alive", output)
