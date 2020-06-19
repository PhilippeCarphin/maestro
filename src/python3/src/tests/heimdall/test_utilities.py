
from tests.path import CSV_DICTIONARY

import unittest

from utilities import get_dictionary_list_from_csv

class TestUtilities(unittest.TestCase):
            
    def test_csv_dictionary(self):
        result=get_dictionary_list_from_csv(CSV_DICTIONARY)
        self.assertEqual(len(result),2)
        self.assertEqual(result[1]["name"],"george")
        