import os
from constants.path import MAESTRO_ROOT, PYTHON3_ROOT

MFLOW_TEST_FOLDER = PYTHON3_ROOT+"tests/mflow_tests/"
HEIMDALL_TEST_FOLDER = PYTHON3_ROOT+"tests/heimdall_tests/"
MAESTRO_TEST_FOLDER = PYTHON3_ROOT+"tests/maestro_tests/"
GENERIC_TEST_FOLDER = PYTHON3_ROOT+"tests/generic_tests/"
MOCK_FILES = MAESTRO_ROOT+"mock_files/"

TMP_FOLDER = MAESTRO_ROOT+"tmp/"
os.makedirs(TMP_FOLDER, exist_ok=True)

BIG_ME_PATH = MOCK_FILES+"complete_experiment/"
TURTLE_ME_PATH = MOCK_FILES+"turtle_experiment/"
BIG_LOOP_ME_PATH = MOCK_FILES+"big_loop_experiment/"
SUBMIT_CHAIN_ME_PATH = MOCK_FILES+"submit-chain-experiment/"
STRANGE_RESOURCES_ME_PATH = MOCK_FILES+"strange-resources/"
GDPS_MINI_ME_PATH = MOCK_FILES+"gdps-mini/"
G0_MINI_ME_PATH = GDPS_MINI_ME_PATH+"g0/"
G1_MINI_ME_PATH = GDPS_MINI_ME_PATH+"g1/"
GV_MINI_ME_PATH = GDPS_MINI_ME_PATH+"verification/"
SWITCH_HOUR_ME_PATH = MOCK_FILES+"switch-datestamp-hour/"
FILE_INDEX_ME_PATH = MOCK_FILES+"file_index/"
DELTA_ME_PATH = MOCK_FILES+"delta-old-new/"
TMP_DELTA_ME_PATH = TMP_FOLDER+"delta-old-new/"

def get_lines_from_file(path, remove_prefix_slash=True):
    "Return a list of stripped strings for each non-empty line in this file."
    with open(path, "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines if line.strip()]
    if remove_prefix_slash:
        lines = [line[1:] if line.startswith("/") else line for line in lines]
    return lines


NODE_PATHS_G0 = get_lines_from_file(MOCK_FILES+"node_paths_g0")
NODE_PATHS_G1 = get_lines_from_file(MOCK_FILES+"node_paths_g1")
NODE_PATHS_COMP_EXP = get_lines_from_file(MOCK_FILES+"node_paths_comp_exp")

NODE_LOG_UTF8_ERROR = MOCK_FILES+"20200604120000_nodelog_utf8_error"
NODE_LOG_TURTLE_DURATION = MOCK_FILES+"nodelog_turtle_duration"
ABSOLUTE_SYMLINK_EXISTS_PATH=TMP_FOLDER+"symlink-to-absolute-existing-target"

RESOURCES_HOME1 = MOCK_FILES+"resources-home1/"
RESOURCES_HOME2 = MOCK_FILES+"resources-home2/"
RESOURCES_HOME3 = MOCK_FILES+"resources-home3/"

CONTEXT_GUESS_HOMES = MOCK_FILES+"homes/"
OPERATIONAL_HOME = CONTEXT_GUESS_HOMES+"smco500"
PARALLEL_HOME = CONTEXT_GUESS_HOMES+"smco501"
OPERATIONAL_SUITES_HOME=CONTEXT_GUESS_HOMES+"smco502"
MINI_SUITES_XML_PATH=OPERATIONAL_HOME+"/xflow.suites.xml"

QSTAT_OUTPUT1_PATH = MOCK_FILES+"qstat-output1"
CMCCONST_OVERRIDE=MOCK_FILES+"cmcconst/"

TURTLE_DATESTAMP1 = "2020040100"

SUITES_WITH_CODES = MOCK_FILES+"suites_with_codes/"
SUITES_WITHOUT_CODES = MOCK_FILES+"suites_without_codes/"
CSV_DICTIONARY = MOCK_FILES+"csv_dictionary.csv"