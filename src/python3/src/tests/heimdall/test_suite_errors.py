import unittest
from tests.path import HEIMDALL_ME_FOLDER
from heimdall.experiment_scanner import ExperimentScanner

class TestSuiteErrors(unittest.TestCase):
            
    def test_simple(self):
        for code in ("e1","e2","e3","e4"):
            path=HEIMDALL_ME_FOLDER+code
            scanner=ExperimentScanner(path,
                                      blocking_errors_is_exception=False)
            msg="experiment path: '%s'"%path
            self.assertIn(code,scanner.codes,msg=msg)