import unittest
from tests.cache import HEIMDALL_ERRORS1_ME
from heimdall.experiment_scanner import ExperimentScanner

class TestSuiteErrors(unittest.TestCase):
            
    def test_missing_folders(self):
        scanner=ExperimentScanner(HEIMDALL_ERRORS1_ME)
        code="e1"
        self.assertIn(code,scanner.codes)
        self.assertIn(code,scanner.messages)