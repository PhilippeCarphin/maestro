#!/usr/bin/python3

import unittest
import sys
from utilities import *

tests = unittest.TestLoader().discover("ssm", pattern ='*.py')
runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
runner.run(tests)
