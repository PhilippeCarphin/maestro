import os

class PATH:
    MOCK_FILES=os.path.dirname(os.path.realpath(__file__))+"/mock_files"
PATH.SAMPLE_EXP1=PATH.MOCK_FILES+"/sample_experiment1"

SSM_DOMAIN_PATH=os.environ["SSM_DOMAIN_PATH"]
SSM_USE_COMMAND=". ssmuse-sh -d %s ; "%SSM_DOMAIN_PATH
MAESTRO_VERSION=SSM_DOMAIN_PATH.split(os.sep)[-1]
MAESTRO_PARAMETERS_FILE=os.environ["HOME"]+"/.suites/.maestro_server_"+MAESTRO_VERSION

"this is a dictionary of simple commands which can be run and should have a successful exit status"
success_commands={"getdef":"getdef -e %s resources FRONTEND"%PATH.SAMPLE_EXP1,
                  "expclean":"expclean -e "+ PATH.SAMPLE_EXP1 +" -d 20191102111111 -l",
                  "scanexp":"scanexp -e "+PATH.SAMPLE_EXP1+" -s current_index_dep",
                  "maestro":"maestro -d 20191102111111 -n /sample/Different_Hosts/IBMTask -s submit -f continue -e "+PATH.SAMPLE_EXP1,
                  "nodesource":"export SEQ_EXP_HOME="+PATH.SAMPLE_EXP1+" ; nodesource -n /sample/Different_Hosts/VAR",
                  "nodelogger":"nodelogger -n /sample/Different_Hosts/IBMTask -s info -m hello -e "+PATH.SAMPLE_EXP1+" -d 20191102111111",
                  "nodeinfo":"nodeinfo -n /sample/Different_Hosts/IBMTask -e "+PATH.SAMPLE_EXP1}
