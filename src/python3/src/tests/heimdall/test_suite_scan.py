import os.path
import unittest

from constants import SCANNER_CONTEXT
from tests.path import SUITES_WITH_CODES, SUITES_WITHOUT_CODES, TURTLE_ME_PATH, G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH, OPERATIONAL_HOME, PARALLEL_HOME, TMP_FOLDER
from heimdall.message_manager import hmm
from heimdall.experiment_scanner import ExperimentScanner
from tests.temp_file_builder import setup_b1_experiment, setup_tmp_smco501_home

QSTAT_QUEUE_OUTPUT="""
Queue              Max   Tot Ena Str   Que   Run   Hld   Wat   Trn   Ext Type
---------------- ----- ----- --- --- ----- ----- ----- ----- ----- ----- ----
prod                 0     0 yes yes     0     0     0     0     0     0 Exec
prod_xxfer           6     0 yes yes     0     0     0     0     0     0 Exec
prod_daemon          0     5 yes yes     0     5     0     0     0     0 Exec
production           0     0 yes yes     0     0     0     0     0     0 Rout
prod_hpnls          20    10 yes yes     0    10     0     0     0     0 Exec
archive              0     0 yes yes     0     0     0     0     0     0 Rout
hpnls               10     0 yes yes     0     0     0     0     0     0 Exec
project              0     0 yes yes     0     0     0     0     0     0 Rout
dev_xxfer            4     0 yes yes     0     0     0     0     0     0 Exec
dev_daemon           0     1 yes yes     0     1     0     0     0     0 Exec
development          0     0 yes yes     0     0     0     0     0     0 Rout
dedicated_bench      0     0 yes yes     0     0     0     0     0     0 Exec
dev                  0   166 yes yes     0   166     0     0     0     0 Exec
ibmbench             0     0 yes yes     0     0     0     0     0     0 Exec
crayadm              0     0 yes yes     0     0     0     0     0     0 Exec
prod_persistent      0     0 yes yes     0     0     0     0     0     0 Rout
prod_p               0   236 yes yes     1   235     0     0     0     0 Exec
xfer               0   236 yes yes     1   235     0     0     0     0 Exec
"""

class TestSuiteScan(unittest.TestCase):        
            
    def test_suites_with_codes(self):
        """
        Test all experiments in 'suites_with_codes' folder.
        
        For example, 'suites_with_codes/e7' experiment has 'e7' code
        """
        
        setup_b1_experiment()
        setup_tmp_smco501_home()
                        
        for code in hmm.codes:
            path=SUITES_WITH_CODES+code
            
            "check that the test folder exists"
            if code!="c3":
                "exclude c3 because that's the error we expect - the folder does not exist"
                msg="Mock experiment for code '%s' does not exist at path '%s'. All codes must have a test case."%(code,path)
                self.assertTrue(os.path.isdir(path),msg=msg)
            
            "override the context, if necessary"
            context=None
            if code in ["e7","e10","w7","w11","w12"]:
                context=SCANNER_CONTEXT.OPERATIONAL
            if code in ["i1"]:
                context=SCANNER_CONTEXT.DEVELOPMENT
                
            "override op/par homes, if necessary"
            parallel_home=PARALLEL_HOME
            if code == "w12":
                parallel_home=TMP_FOLDER+"smco501"
            
            scanner=ExperimentScanner(path,
                                      context=context,
                                      operational_home=OPERATIONAL_HOME,
                                      parallel_home=parallel_home,
                                      critical_error_is_exception=False,
                                      debug_qstat_queue_override=QSTAT_QUEUE_OUTPUT)
            
            msg="Experiment path: '%s'"%path
            self.assertIn(code,scanner.codes,msg=msg)
            
    def test_suites_without_codes(self):
        """
        Test all experiments in 'suites_without_codes' folder.
        
        Tor example, 'suites_without_codes/e7' experiment does not have 'e7' code
        """
        
        unused_folders=[p for p in os.listdir(SUITES_WITHOUT_CODES) if os.path.isdir(SUITES_WITHOUT_CODES+p)]
        
        for code in hmm.codes:
            path=SUITES_WITHOUT_CODES+code
            if not os.path.isdir(path):
                continue
            
            if code in unused_folders:
                unused_folders.remove(code)
                
                msg="Experiment path: '%s'"%path
                scanner=ExperimentScanner(path,
                                          critical_error_is_exception=False,
                                          debug_qstat_queue_override=QSTAT_QUEUE_OUTPUT)
                self.assertNotIn(code,scanner.codes,msg=msg)
            
    def test_good_suite(self):
        """
        All good suites do not have any codes, 
        unless they are on the expected list
        """
        
        paths=[TURTLE_ME_PATH,G0_MINI_ME_PATH,G1_MINI_ME_PATH,GV_MINI_ME_PATH]
        
        "since the good suites are minimal, never look for these codes"
        ignore_codes=["w1", "w2"]
        
        """
        key is experiment path
        value is list of codes that we allow because it exists in the real suite
        """
        expected_errors={G1_MINI_ME_PATH:["e5"]}
        expected_errors={key:set(value) for key,value in expected_errors.items()}
        
        for path in paths:
            scanner=ExperimentScanner(path,
                                      critical_error_is_exception=False,
                                      debug_qstat_queue_override=QSTAT_QUEUE_OUTPUT)
            msg="Experiment path: '%s'"%path
            msg+="\n\n"+scanner.get_report_text()
            
            "never look for codes we want to ignore"
            result=scanner.codes
            for code in ignore_codes:
                if code in result:
                    result.remove(code)
                    
            expected=expected_errors.get(path,set())
            self.assertEqual(result,expected,msg=msg)