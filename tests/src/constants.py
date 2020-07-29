"""
This file should not be changed for different platforms or installations.
See also "config.py".
"""

import os

d=os.path.dirname
class PATH:
    MOCK_FILES=d(d(os.path.realpath(__file__)))+"/mock_files"
    SSM_DOMAIN=os.environ["MAESTRO_TEST_SSM_DOMAIN_PATH"]
PATH.SAMPLE_EXP1=PATH.MOCK_FILES+"/sample_experiment1"

SSM_USE_COMMAND=". ssmuse-sh -d %s ; "%PATH.SSM_DOMAIN
MAESTRO_VERSION=PATH.SSM_DOMAIN.split(os.sep)[-1]
MAESTRO_PARAMETERS_FILE=os.environ["HOME"]+"/.suites/.maestro_server_"+MAESTRO_VERSION

"this is a dictionary of simple commands which can be run and should have a successful exit status"
success_commands={"getdef":"getdef -e %s resources FRONTEND"%PATH.SAMPLE_EXP1,
                  "expclean":"expclean -e "+ PATH.SAMPLE_EXP1 +" -d 20191102111111 -l",
                  "scanexp":"scanexp -e "+PATH.SAMPLE_EXP1+" -s current_index_dep",
                  "maestro":"maestro -d 20191102111111 -n /sample/Different_Hosts/IBMTask -s submit -f continue -e "+PATH.SAMPLE_EXP1,
                  "nodesource":"export SEQ_EXP_HOME="+PATH.SAMPLE_EXP1+" ; nodesource -n /sample/Different_Hosts/VAR",
                  "nodelogger":"nodelogger -n /sample/Different_Hosts/IBMTask -s info -m hello -e "+PATH.SAMPLE_EXP1+" -d 20191102111111",
                  "nodeinfo":"nodeinfo -n /sample/Different_Hosts/IBMTask -e "+PATH.SAMPLE_EXP1}

def create_config_py_if_missing():
    template="""# This is an automatically generated template for config. You may want to change the values in this file. See also "tests/constants.py
    
# the option given to mserver for machine, for example "maestro2" or "eccc-ppp4"
MSERVER_MACHINE="""+os.environ.get("TRUE_HOST","eccc-ppp4")
    config_path=os.path.dirname(os.path.realpath(__file__))+"/config.py"
    if not os.path.isfile(config_path):
        with open(config_path,"w") as f:
            f.write(template)

create_config_py_if_missing()
