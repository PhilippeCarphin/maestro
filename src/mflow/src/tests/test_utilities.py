import unittest

from constants import TURTLE_ME_PATH
from utilities import get_variable_value_from_file, superstrip
from maestro import get_latest_yyyymmddhh_from_experiment_path, get_yyyymmddhh, get_day_of_week

class TestUtilities(unittest.TestCase):
            
    def test_get_variable_value_from_file(self):
        path=TURTLE_ME_PATH+"/resources/resources.def"
        result=get_variable_value_from_file(path,"FRONTEND")
        self.assertEqual(result,"turtle-frontend")
        
    def test_get_day_of_week(self):
        expected=4
        result=get_day_of_week("20200514")
        self.assertEqual(result,expected)
        
        result=get_day_of_week("2020051400")
        self.assertEqual(result,expected)
        
        result=get_day_of_week("20200514000000")
        self.assertEqual(result,expected)
        
    def test_get_datestamp(self):
        result=get_latest_yyyymmddhh_from_experiment_path(TURTLE_ME_PATH)
        self.assertEqual(result,"2020040100")
        
        result=get_latest_yyyymmddhh_from_experiment_path("/nothing/is/here/wut")
        self.assertEqual(result,"")
        
        "does not crash"
        get_yyyymmddhh()
        
    def test_superstrip(self):
        result=superstrip("aabbcdbbaa","ab")
        self.assertEqual(result,"cd")
        
        result=superstrip("aabbcdbbaa","xyz")
        self.assertEqual(result,"aabbcdbbaa")