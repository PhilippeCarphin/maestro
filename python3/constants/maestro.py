
class NODE_TYPE:
    TASK = "task"
    MODULE = "module"
    FAMILY = "family"
    SWITCH = "switch"
    SWITCH_ITEM = "switch_item"
    LOOP = "loop"
    NPASS_TASK = "npass_task"

NODE_TYPES = (NODE_TYPE.TASK, NODE_TYPE.MODULE, NODE_TYPE.FAMILY, NODE_TYPE.SWITCH, NODE_TYPE.SWITCH_ITEM, NODE_TYPE.LOOP, NODE_TYPE.NPASS_TASK)

class NODE_STATUS():
    """
    whenever possible, these values align with the file suffixes in "sequencing/status" files
    """
    ABORT = "abort"
    SUBMIT_FAILURE = "submit-failure"
    END = "end"
    BEGIN = "begin"
    WAITING = "waiting"
    NOT_STARTED = "not-started"
    CATCHUP = "catchup"

NODE_STATUSES = (NODE_STATUS.ABORT, NODE_STATUS.SUBMIT_FAILURE, NODE_STATUS.END, NODE_STATUS.BEGIN, NODE_STATUS.WAITING, NODE_STATUS.NOT_STARTED, NODE_STATUS.CATCHUP)

class SWITCH_TYPE():
    HOUR = "datestamp_hour"
    DAY_OF_WEEK = "day_of_week"

CONTAINER_TAGS = ("loop", "switch", "family", "module")

REQUIRED_LOG_FOLDERS= ("listings", "logs", "sequencing")
EXPERIMENT_LOG_FOLDERS = ("listings", "logs", "sequencing", "stats")

"Maestro executables which are commonly used in tasks."
TASK_MAESTRO_BINS=["maestro","nodeinfo","nodelogger"]