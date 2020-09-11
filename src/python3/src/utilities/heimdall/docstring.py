
from constants import VERSION
from utilities.maestro.path import get_exp_home_from_pwd
from utilities.heimdall.language import get_language_from_environment

def adjust_docstring(doc):
    exp = get_exp_home_from_pwd()
    language=get_language_from_environment()
    return doc % (VERSION, exp, language)
