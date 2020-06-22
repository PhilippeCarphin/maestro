import os.path
import unittest
from tests.path import HEIMDALL_ME_FOLDER, TURTLE_ME_PATH, G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH
from heimdall.message_manager import hmm
from heimdall.experiment_scanner import ExperimentScanner

class TestSuiteScan(unittest.TestCase):
            
    def test_heimdall_mock_experiments(self):
        """
        All codes in the heimdall message manager should have a corresponding
        experiment in mock files that produces that code.
        """
        for code in hmm.codes:
            path=HEIMDALL_ME_FOLDER+code
            
            msg="Mock experiment for code '%s' does not exist at path '%s'. All codes must have a test case."%(code,path)
            if code!="c3":
                "exclude c3 because that's an error where the folder does not exist"
                self.assertTrue(os.path.isdir(path),msg=msg)
            
            scanner=ExperimentScanner(path,
                                      critical_error_is_exception=False)
            msg="Experiment path: '%s'"%path
            self.assertIn(code,scanner.codes,msg=msg)
    
    def test_good_suite(self):
        "no errors in these suites"
        
        paths=[TURTLE_ME_PATH,G0_MINI_ME_PATH,G1_MINI_ME_PATH,GV_MINI_ME_PATH]
        for path in paths:
            scanner=ExperimentScanner(path,
                                      critical_error_is_exception=False)
            msg="Experiment path: '%s'"%path
            self.assertFalse(scanner.codes,msg=msg)