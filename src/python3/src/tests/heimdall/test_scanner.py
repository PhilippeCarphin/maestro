import unittest
from tests.path import FILE_INDEX_ME_PATH
from heimdall.experiment_scanner import ExperimentScanner
from utilities import pretty_kwargs

class TestScanner(unittest.TestCase):
            
    def test_file_index(self):
        self.maxDiff=None
        
        p=FILE_INDEX_ME_PATH
        scanner=ExperimentScanner(p)
        
        expected=[p+"modules/main/flow.xml",
                  p+"resources/main/task1.xml",
                  p+"resources/main/task2.xml"]
        result=scanner.xml_files
        msg=pretty_kwargs(result=result,expected=expected)
        self.assertEqual(result,expected,msg=msg)
        
        expected=[p+"modules/main/123_bad_task_name.tsk",
                  p+"modules/main/task1.tsk",
                  p+"modules/main/task2.tsk"]
        self.assertEqual(scanner.task_files,expected)
        
        expected=[p+"modules/main/task1.cfg"]
        self.assertEqual(scanner.config_files,expected)
        
        expected=[p+"modules/main/flow.xml"]
        self.assertEqual(scanner.flow_files,expected)
    

