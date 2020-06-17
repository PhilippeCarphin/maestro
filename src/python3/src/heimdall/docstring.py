
from constants import HEIMDALL_VERSION
from maestro.path import get_exp_home_from_pwd

def adjust_docstring(doc):
    exp=get_exp_home_from_pwd()
    return doc%(HEIMDALL_VERSION,exp)