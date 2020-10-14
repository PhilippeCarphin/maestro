import os

d = os.path.dirname
MAESTRO_ROOT = d(d(d(os.path.realpath(__file__))))+os.sep
PYTHON3_ROOT = MAESTRO_ROOT+"python3/"
HEIMDALL_MESSAGE_CSV = MAESTRO_ROOT+"csv/message_codes.csv"
HEIMDALL_CONTENT_CHECKS_CSV = MAESTRO_ROOT+"csv/file_content_checks.csv"

HISTORY_FOLDER = MAESTRO_ROOT+"/history/"
TMP_FOLDER = os.environ["HOME"]+"/tmp/mflow/"
LOG_FOLDER = os.environ["HOME"]+"/logs/"
BIN_FOLDER = MAESTRO_ROOT+"bin/"
DOC_FOLDER = MAESTRO_ROOT+"doc/"
DEFAULT_CONFIG_PATH = MAESTRO_ROOT+"config/mflow/default"

HEIMDALL_CODES_DOC_EN=DOC_FOLDER+"en/heimdall_codes.md"
HEIMDALL_CODES_DOC_FR=DOC_FOLDER+"fr/heimdall_codes.md"

# To change this value, one must also change it in the bash wrapper script bin/mflow
TMP_BASH_WRAPPER_COMMAND_FILE_PREFIX = TMP_FOLDER+".tmp-bash-wrapper-command-"

os.makedirs(TMP_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
