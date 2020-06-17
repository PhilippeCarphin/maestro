import unittest
import sys
from constants import TESTS_FOLDER
from mflow.utilities import get_config

def filter_tests_with_whitelist(tests,whitelist):
    """
    Converting a TestSuite to string is messy but at least this method is simple and won't accidentally filter.
    
    TestSuite to string example:
        
    <unittest.suite.TestSuite tests=[<unittest.suite.TestSuite tests=[<test_maestro_experiment.TestMaestroExperiment testMethod=test_children>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_complete_experiment_nodes>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_loop>, <test_maestro_experiment.TestMaestroExperiment testMethod=test_module>]>]>
    """
    results=[]
    
    for test in tests:
        for white in whitelist:
            if white in str(test):
                results.append(test)
                break
            
    return results

def run_tests(verbose=False,test_filter=None):
    
    if test_filter:
        test_filter="*"+test_filter+"*"
    else:
        test_filter="test*.py"        
    
    tests = unittest.TestLoader().discover(TESTS_FOLDER,pattern=test_filter)
        
    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    runner.run(tests)


def get_test_config(**kwargs):
    "easy way to get a full config, with some changes, for testing"
    config=get_config()
    for key in kwargs:
        config[key]=kwargs[key]
    return config
    