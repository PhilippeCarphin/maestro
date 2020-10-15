#!venv/bin/python3

from constants import *
from utilities import *
from tests.path import *
from heimdall import *
from maestro_experiment import *
from heimdall.path import *

context=SCANNER_CONTEXT.TEST
path=SUITES_WITHOUT_CODES+"b026"
path=G1_MINI_ME_PATH
path=SUITES_WITH_CODES+"w036"

scanner=ExperimentScanner(path,
                          context=context,
                          operational_home=OPERATIONAL_HOME,
                          parallel_home=PARALLEL_HOME,
                          operational_suites_home=OPERATIONAL_SUITES_HOME,
                          debug_hub_filecount=10,
                          debug_hub_ignore_age=True)
scanner.print_report(level="w",max_repeat=3)