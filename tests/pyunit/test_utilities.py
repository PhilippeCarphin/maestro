import unittest
from utilities import *

"""
Utilities are generic functions that could be used, unmodified, in other projects.
"""

class TestUtilities(unittest.TestCase):

    def test_get_output(self):
        result = get_output("ls", use_popen = True)
        self.assertIs(type(result), tuple)
        output,status=result
        self.assertIs(type(output), str)
        self.assertIs(type(status), int)
