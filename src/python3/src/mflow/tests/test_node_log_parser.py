import unittest

from maestro import NodeLogParser
from constants import  NODE_LOG_UTF8_ERROR

class TestNodeLogParser(unittest.TestCase):
    
    def test_utf8_open_error(self):
        nlp=NodeLogParser(NODE_LOG_UTF8_ERROR)