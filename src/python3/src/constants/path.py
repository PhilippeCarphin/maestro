import os

d = os.path.dirname
MAESTRO_ROOT = d(d(d(d(d(os.path.realpath(__file__))))))+os.sep
MFLOW_ROOT = MAESTRO_ROOT+"src/python3/"
HEIMDALL_ROOT = MAESTRO_ROOT+"src/python3/"
HEIMDALL_MESSAGE_CSV = HEIMDALL_ROOT+"csv/message_codes.csv"
HEIMDALL_CONTENT_CHECKS_CSV = HEIMDALL_ROOT+"csv/file_content_checks.csv"

HISTORY_FOLDER = MFLOW_ROOT+"/history/"
TMP_FOLDER = os.environ["HOME"]+"/tmp/mflow/"
LOG_FOLDER = os.environ["HOME"]+"/logs/"
BIN_FOLDER = MFLOW_ROOT+"/bin/"
DEFAULT_CONFIG_PATH = MFLOW_ROOT+"/config/default"
TEMPLATE_FOLDER = MFLOW_ROOT+"templates/"

# To change this value, one must also change it in the bash wrapper script bin/mflow
TMP_BASH_WRAPPER_COMMAND_FILE_PREFIX = TMP_FOLDER+".tmp-bash-wrapper-command-"

os.makedirs(TMP_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
