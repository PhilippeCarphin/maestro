
"""
To speed up unit tests, frequently used maestro experiments can be parsed just once here.

Tests that use the cache must be smart enough never to modify these instances.
"""

from maestro_experiment import MaestroExperiment
from tests.path import G0_MINI_ME_PATH, G1_MINI_ME_PATH, GV_MINI_ME_PATH, BIG_ME_PATH, TURTLE_ME_PATH, SUBMIT_CHAIN_ME_PATH, STRANGE_RESOURCES_ME_PATH

print("'%s' is building MaestroExperiment cache."%__name__)

"""
user_home is empty so that running tests as different users never uses 
their different home overrides, etc.
"""
G0_MINI_ME=MaestroExperiment(G0_MINI_ME_PATH,user_home="")
G1_MINI_ME=MaestroExperiment(G1_MINI_ME_PATH,user_home="")
GV_MINI_ME=MaestroExperiment(GV_MINI_ME_PATH,user_home="")
BIG_ME=MaestroExperiment(BIG_ME_PATH,user_home="")
TURTLE_ME=MaestroExperiment(TURTLE_ME_PATH,user_home="")
SUBMIT_CHAIN_ME=MaestroExperiment(SUBMIT_CHAIN_ME_PATH,user_home="")
STRANGE_RESOURCES_ME=MaestroExperiment(STRANGE_RESOURCES_ME_PATH,user_home="")