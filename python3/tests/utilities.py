
import unittest
import sys
from tests.path import MFLOW_TEST_FOLDER, HEIMDALL_TEST_FOLDER, MAESTRO_TEST_FOLDER, GENERIC_TEST_FOLDER
from mflow import get_mflow_config

def filter_tests_with_whitelist(tests, whitelist):
    """
    Converting a TestSuite to string is messy but at least this method is simple and won't accidentally filter.

    TestSuite to string example:

    <unittest.suite.TestSuite tests=[<unittest.suite.TestSuite tests=[<test_maestro_experiment.TestMaestroExperiment testMethod=test_children>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_complete_experiment_nodes>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_loop>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_module>]>]>
    """
    results = []

    for test in tests:
        for white in whitelist:
            if white in str(test):
                results.append(test)
                break

    return results


def run_tests(test_mflow=True,
              test_heimdall=True,
              test_maestro=True,
              verbose=False,
              test_filter=None):

    if test_filter:
        test_filter = "*"+test_filter+"*"
    else:
        test_filter = "test*.py"
        
    "load the appropriate subset of test scripts"
    test_suites=[]
    path_to_bool={MFLOW_TEST_FOLDER:test_mflow,
                  HEIMDALL_TEST_FOLDER:test_heimdall,
                  MAESTRO_TEST_FOLDER:test_maestro,
                  GENERIC_TEST_FOLDER:True}
    for path,b in path_to_bool.items():
        if b:
            test_loader=unittest.TestLoader()
            test_suites.append(test_loader.discover(path, pattern=test_filter))
    
    "combine suites"
    combined=unittest.TestSuite(test_suites)
    
    "run tests"
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(combined)

def get_test_config(**kwargs):
    "easy way to get a full config, with some changes, for testing"
    config = get_mflow_config()
    for key in kwargs:
        config[key] = kwargs[key]
    return config
