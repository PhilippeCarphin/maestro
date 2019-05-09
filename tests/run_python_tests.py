#!/usr/bin/python3

import unittest,sys,os
from utilities import *

tests = unittest.TestLoader().discover("pyunit", pattern ='*.py')
runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
runner.run(tests)
