#!/usr/bin/python3

import unittest,sys,os
from utilities.utils import *

tests = unittest.TestLoader().discover("shell_test_suites", pattern ='*.py')
runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
runner.run(tests)
