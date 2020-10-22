
import os
from constants import VERSION, MAX_HUB_SCAN_SECONDS
from maestro.path import get_exp_home_from_pwd
from heimdall.language import get_language_from_environment

def adjust_docstring(doc):
    exp = get_exp_home_from_pwd()
    language=get_language_from_environment()
    user_home=os.environ.get("HOME","")
    return doc.format(version=VERSION,
                      experiment_path=exp,
                      language=language,
                      max_hub_seconds=MAX_HUB_SCAN_SECONDS,
                      user_home=user_home)
