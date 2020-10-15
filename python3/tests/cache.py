
"""
To speed up unit tests, frequently used maestro experiments can be parsed just once here.

Tests that use the cache must be smart enough never to modify these instances.
"""

from functools import lru_cache
from maestro_experiment import MaestroExperiment
from heimdall import ExperimentScanner
from tests.path import G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH, BIG_ME_PATH, TURTLE_ME_PATH, SUBMIT_CHAIN_ME_PATH, STRANGE_RESOURCES_ME_PATH, SWITCH_HOUR_ME_PATH
from tests.path import QSTAT_OUTPUT1_PATH

@lru_cache(maxsize=1000)
def get_experiment_from_cache(*args, **kwargs):
    "See get_scanner_from_cache"
    return MaestroExperiment(*args, **kwargs)

@lru_cache(maxsize=1000)
def get_scanner_from_cache(*args, **kwargs):
    """
    Calling:
        get_scanner_from_cache( ... )
    is identical to:
        ExperimentScanner( ... )    
    except if a scan has already happened for these exact arguments, returns that
    cached scanner instead.
    
    This is useful because the realpath to one test experiment may apply to
    many different scan codes we want to verify.
    """
    return ExperimentScanner(*args, **kwargs)

print("'%s' is building MaestroExperiment cache." % __name__)

"""
user_home is empty so that running tests as different users never uses 
their different home overrides, etc.
"""
G0_MINI_ME = get_experiment_from_cache(G0_MINI_ME_PATH, user_home="")
G1_MINI_ME = get_experiment_from_cache(G1_MINI_ME_PATH, user_home="")
GV_MINI_ME = get_experiment_from_cache(GV_MINI_ME_PATH, user_home="")
BIG_ME = get_experiment_from_cache(BIG_ME_PATH, user_home="")
TURTLE_ME = get_experiment_from_cache(TURTLE_ME_PATH, user_home="")
SUBMIT_CHAIN_ME = get_experiment_from_cache(SUBMIT_CHAIN_ME_PATH, user_home="")
STRANGE_RESOURCES_ME = get_experiment_from_cache(STRANGE_RESOURCES_ME_PATH, user_home="")
SWITCH_HOUR_ME = get_experiment_from_cache(SWITCH_HOUR_ME_PATH, user_home="")

with open(QSTAT_OUTPUT1_PATH, "r") as f:
    QSTAT_CMD_OUTPUT = f.read()
