import unittest

from utilities.maestro import get_intervals_from_status_path
from tests.path import MOCK_FILES

class TestHourIntervals(unittest.TestCase):
    
    def test_get_intervals_from_status_path(self):
        path=MOCK_FILES+"status-summary-suite/sequencing/status/"
        result=get_intervals_from_status_path(path)
        expected=("00","12")
        self.assertEqual(result,expected)
        