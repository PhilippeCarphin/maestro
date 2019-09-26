import os

class PATH:
    MOCK_FILES="mock_files"
    SAMPLE_EXP1="mock_files/sample_experiment1"

SSM_DOMAIN_PATH=os.environ["SSM_DOMAIN_PATH"]
SSM_USE_COMMAND=". ssmuse-sh -d %s ; "%SSM_DOMAIN_PATH

"this is a dictionary of simple commands which can be run and should have a successful exist status"
success_commands={"getdef":"getdef -e %s resources FRONTEND"%PATH.SAMPLE_EXP1,
                  "expclean":"expclean -e "+ PATH.SAMPLE_EXP1 +" -d 20191102111111 -l",
                  "scanexp":"scanexp -e "+PATH.SAMPLE_EXP1+" -s current_index_dep",
                  "maestro":"maestro -d 20191102111111 -n /sample/Different_Hosts/IBMTask -s submit -f continue -e "+PATH.SAMPLE_EXP1,
                  "nodesource":"nodesource -n /sample/Different_Hosts/VAR -e "+PATH.SAMPLE_EXP1,
                  "nodelogger":"nodelogger -n /sample/Different_Hosts/IBMTask -s info -m hello -e "+PATH.SAMPLE_EXP1+" -d 20191102111111",
                  "nodeinfo":"nodeinfo -n /sample/Different_Hosts/IBMTask -e "+PATH.SAMPLE_EXP1,
                  "madmin":"madmin -i"}
