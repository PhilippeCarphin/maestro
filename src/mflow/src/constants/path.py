import os

d=os.path.dirname
PROJECT_ROOT=d(d(d(os.path.realpath(__file__))))+os.sep
HISTORY_FOLDER=PROJECT_ROOT+"/history/"
TMP_FOLDER=os.environ["HOME"]+"/tmp/mflow/"
LOG_FOLDER=os.environ["HOME"]+"/logs/mflow/"
BIN_FOLDER=PROJECT_ROOT+"/bin/"
DEFAULT_CONFIG_PATH=PROJECT_ROOT+"/config/default"
TEMPLATE_FOLDER=PROJECT_ROOT+"templates/"

# To change this value, one must also change it in the bash wrapper script bin/mflow
TMP_BASH_WRAPPER_COMMAND_FILE_PREFIX=TMP_FOLDER+".tmp-bash-wrapper-command-"

def mkdir_p(path):
    "behaves just like 'mkdir -p' "
    try:
        os.makedirs(path)
    except:
        pass
if not os.path.isdir(TMP_FOLDER):
    mkdir_p(TMP_FOLDER)