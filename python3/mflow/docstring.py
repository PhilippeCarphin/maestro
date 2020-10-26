import os.path
import os

from constants import DEFAULT_CONFIG_PATH, VERSION
from maestro.path import get_exp_home_from_pwd


def get_default_config_path():
    "If config exists in home, return that, otherwise return project default."

    home_config = os.environ["HOME"]+"/.mflowrc"
    if os.path.isfile(home_config):
        return home_config
    return DEFAULT_CONFIG_PATH


def adjust_docstring(doc):
    exp = get_exp_home_from_pwd()
    home_path = os.environ["HOME"]
    config_path = get_default_config_path()
    return doc % (VERSION,
                  DEFAULT_CONFIG_PATH,
                  exp,
                  home_path,
                  config_path)
