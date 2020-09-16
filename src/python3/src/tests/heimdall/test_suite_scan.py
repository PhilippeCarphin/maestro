import os.path
import unittest
from functools import lru_cache

from constants import SCANNER_CONTEXT
from tests.path import SUITES_WITH_CODES, SUITES_WITHOUT_CODES, TURTLE_ME_PATH, G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH, OPERATIONAL_HOME, PARALLEL_HOME, OPERATIONAL_SUITES_HOME, TMP_FOLDER, QSTAT_OUTPUT1_PATH, CMCCONST_OVERRIDE
from heimdall.message_manager import hmm
from heimdall.experiment_scanner import ExperimentScanner
from tests.test_file_builder import setup_tricky_mock_files, setup_tmp_experiment1, setup_tmp_experiment2, setup_tmp_experiment3, setup_tmp_smco501_home, setup_tmp_git_author_repo
from tests.cache import QSTAT_CMD_OUTPUT

@lru_cache(maxsize=1000)
def get_scanner_from_cache(*args, **kwargs):
    """
    Calling:
        get_scanner_from_cache( ... )
    is identical to:
        ExperimentScanner( ... )    
    except if a scan has already happened for these exact arguments, returns that
    cached scanner instead.
    
    This is useful because the realpath to one test experiment may apply to
    many different scan codes we want to verify.
    """
    return ExperimentScanner(*args, **kwargs)

class TestSuiteScan(unittest.TestCase):

    def test_suites_with_codes(self):
        """
        Test all experiments in 'suites_with_codes' folder.

        For example, 'suites_with_codes/e007' experiment has 'e7' code
        
        Also, almost all codes must have an example suite in this folder.
        """

        setup_tricky_mock_files()
        setup_tmp_experiment1()
        setup_tmp_experiment3()
        setup_tmp_smco501_home()
        setup_tmp_git_author_repo(always_recreate=True)
        
        folders=os.listdir(SUITES_WITH_CODES)
        
        "iterate over every code"
        for code in hmm.codes:
            
            for folder in folders:
                
                """
                Some codes have more than one folder, like 'e025' and 'e025-b'
                For every code, check if every folder starts with it.
                """
                if not folder.startswith(code):
                    continue
                
                path=SUITES_WITH_CODES+folder
                realpath=os.path.realpath(path)
    
                if code == "e016":
                    """
                    ignore the git repo check, hard to guarantee tmp files setup
                    outside repo have no git repo
                    """
                    continue
    
                if code != "c003":
                    "exclude c003 because that's the error we expect - the folder does not exist"
                    msg = "Mock experiment for code '%s' does not exist at path '%s'. All codes must have a test case." % (code, path)
                    self.assertTrue(os.path.isdir(path), msg=msg)
    
                "override the context, if necessary"
                context = None
                debug_op_username_override = None
                if code in ["e007", "e010", "w007", "w011", "w012", "e014", 
                            "e016", "w015", "w022", "w023", "w024", "e024",
                            "e025", "w025", "w028"]:
                    context = SCANNER_CONTEXT.OPERATIONAL
                if code in ["i001", "i007"]:
                    context = SCANNER_CONTEXT.DEVELOPMENT
                if code in ["w023"]:
                    debug_op_username_override=os.environ["USER"]
    
                "override op/par homes, if necessary"
                parallel_home = PARALLEL_HOME
                if code == "w012":
                    parallel_home = TMP_FOLDER+"smco501"
    
                scanner = get_scanner_from_cache(realpath,
                                            context=context,
                                            operational_home=OPERATIONAL_HOME,
                                            parallel_home=parallel_home,
                                            operational_suites_home=OPERATIONAL_SUITES_HOME,
                                            critical_error_is_exception=False,
                                            debug_qstat_output_override=QSTAT_CMD_OUTPUT,
                                            debug_cmcconst_override=CMCCONST_OVERRIDE,
                                            debug_op_username_override=debug_op_username_override)
    
                msg = "\n\nexperiment path:\n    %s\nrealpath:\n    %s\n" % (path,realpath)
                self.assertIn(code, scanner.codes, msg=msg)

    def test_suites_without_codes(self):
        """
        Test all experiments in 'suites_without_codes' folder.

        Tor example, 'suites_without_codes/e7' experiment does not have 'e7' code
        """
        
        setup_tmp_experiment2()
        
        unused_folders = [p for p in os.listdir(SUITES_WITHOUT_CODES) if os.path.isdir(SUITES_WITHOUT_CODES+p)]

        for code in hmm.codes:
            path = SUITES_WITHOUT_CODES+code
            realpath=os.path.realpath(path)
            
            if not os.path.isdir(path):
                continue

            if code in unused_folders:
                unused_folders.remove(code)

                scanner = get_scanner_from_cache(realpath,
                                            critical_error_is_exception=False,
                                            operational_home=OPERATIONAL_HOME,
                                            parallel_home=PARALLEL_HOME,
                                            operational_suites_home=OPERATIONAL_SUITES_HOME,
                                            debug_qstat_output_override=QSTAT_CMD_OUTPUT)

                msg = "Experiment path:\n    %s\nrealpath:\n    %s\n" % (path,realpath)
                msg += "\n\n"+scanner.get_report_text()

                self.assertNotIn(code, scanner.codes, msg=msg)

    def test_good_suite(self):
        """
        All good suites do not have any codes, 
        unless they are on the expected list
        """

        paths = [TURTLE_ME_PATH, G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH]

        """
        "good" suites are really just "decent" suites.
        Even good suites may have these codes so ignore them.
        This may also be due to real path is a test suite, or git repo stuff.
        """
        ignore_codes = ["w001", "w002", "i002", "e016", "i004", "b009", "i006", 
                        "b014", "b017", "e021", "i009", "b025", "i010", "b027",
                        "b028", "w031"]

        """
        like ignore_codes, but suite specific
        """
        expected_errors = {G0_MINI_ME_PATH: ["b006", "b008", "b016"],
                           G1_MINI_ME_PATH: ["b006", "e005", "b008", "b016"],
                           GV_MINI_ME_PATH: ["b008", "b016"]}
        expected_errors = {key: set(value) for key, value in expected_errors.items()}

        for path in paths:
            realpath=os.path.realpath(path)
            scanner = get_scanner_from_cache(realpath,
                                        critical_error_is_exception=False,
                                        debug_qstat_output_override=QSTAT_CMD_OUTPUT)
            msg = "Experiment path:\n    %s\nrealpath:\n    %s\n" % (path,realpath)
            msg += "\n\n"+scanner.get_report_text(max_repeat=5)

            "never look for codes we want to ignore"
            result = scanner.codes
            for code in ignore_codes:
                if code in result:
                    result.remove(code)

            expected = expected_errors.get(path, set())
            self.assertEqual(result, expected, msg=msg)