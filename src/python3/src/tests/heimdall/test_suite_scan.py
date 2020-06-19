import os.path
import unittest
from tests.path import HEIMDALL_ME_FOLDER
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
            if code!="e4":
                "exclude e4 because that's an error where the folder does not exist"
                self.assertTrue(os.path.isdir(path),msg=msg)
            
            scanner=ExperimentScanner(path,
                                      blocking_errors_is_exception=False)
            msg="Experiment path: '%s'"%path
            self.assertIn(code,scanner.codes,msg=msg)