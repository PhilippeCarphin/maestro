
NODELOGGER_SIGNALS = ["abort",
                      "begin",
                      "end",
                      "info",
                      "infox",
                      "init",
                      "submit"]


class SCANNER_CONTEXT():
    OPERATIONAL = "operational"
    PREOPERATIONAL = "preoperational"
    PARALLEL = "parallel"
    DEVELOPMENT = "development"
    TEST = "test"


SCANNER_CONTEXTS = [SCANNER_CONTEXT.OPERATIONAL,
                    SCANNER_CONTEXT.PREOPERATIONAL,
                    SCANNER_CONTEXT.PARALLEL,
                    SCANNER_CONTEXT.DEVELOPMENT,
                    SCANNER_CONTEXT.TEST]

EXPECTED_CONFIG_STATES = {SCANNER_CONTEXT.OPERATIONAL: {"DISSEM_STATE": "ON",
                                                        "PREOP_STATE": "OFF"},
                          SCANNER_CONTEXT.PREOPERATIONAL: {"DISSEM_STATE": "ON",
                                                           "PREOP_STATE": "ON"},
                          SCANNER_CONTEXT.PARALLEL: {"DISSEM_STATE": "ODD",
                                                     "PREOP_STATE": "OFF"}}

"""
These pairs in $EXPERIMENT/hub should have nearly identical targets.
"""
HUB_PAIRS = [["banting", "daley"],
             ["hare", "brooks"]]

OPERATIONAL_USERNAME="smco500"