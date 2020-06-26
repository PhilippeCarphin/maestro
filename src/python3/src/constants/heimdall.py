
class MESSAGE_LEVEL():
    BEST_PRACTICE="best practice"
    INFO="info"
    WARNING="warning"
    ERROR="error"

NODELOGGER_SIGNALS=["abort",
                    "begin",
                    "end",
                    "info",
                    "infox",
                    "init",
                    "submit"]

class SCANNER_CONTEXT():
    OPERATIONAL="operational"
    PREOPERATIONAL="preoperational"
    PARALLEL="parallel"
    DEVELOPMENT="development"
    TEST="test"
SCANNER_CONTEXTS=[SCANNER_CONTEXT.OPERATIONAL,
                SCANNER_CONTEXT.PREOPERATIONAL,
                SCANNER_CONTEXT.PARALLEL,
                SCANNER_CONTEXT.DEVELOPMENT,
                SCANNER_CONTEXT.TEST]