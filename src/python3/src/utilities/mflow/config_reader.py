import os.path
from constants.mflow import KEYBOARD_NAVIGATION_TYPE
from constants import DEFAULT_CONFIG_PATH
from utilities.generic import clamp


def get_mflow_config(path=None, apply_defaults=True):
    """
    Always returns a complete configuration dictionary.

    If no file, load the default.

    apply_defaults: If file fails to parse or is missing values, use the default values.
    """

    if not path:
        path = DEFAULT_CONFIG_PATH

    if not os.path.isfile(path):
        raise ValueError("get_mflow_config path is not a file: '%s'" % path)

    with open(path, "r") as f:
        lines = f.readlines()

    "only look at non-comment lines with assignments"
    lines = [line.strip() for line in lines if "=" in line and not line.strip().startswith("#")]

    config = {}
    for line in lines:
        key = line.split("=")[0].strip()
        value = line[line.index("=")+1:].strip()
        config[key] = value

    "if enum is bad, use the first as default"
    enums = {"KEYBOARD_NAVIGATION": [KEYBOARD_NAVIGATION_TYPE.TREE,
                                     KEYBOARD_NAVIGATION_TYPE.COORDINATE]}
    for e in enums:
        if config[e] not in enums[e]:
            config[e] = enums[e][0]

    "use defaults for any missing values"
    if apply_defaults:
        default_config = get_mflow_config(DEFAULT_CONFIG_PATH, apply_defaults=False)
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]

    cast_config(config)

    return config


def cast_config(config):
    "where appropriate, replaces 'true' with boolean, or number strings with numbers."

    booleans = ["FLOW_NODE_SHOW_TYPE", "VIEW_MAESTRO_COMMAND_OUTPUT"]
    floats = []
    integers = ["FLOW_STATUS_REFRESH_SECONDS",
                "NODE_MARGIN_BOTTOM",
                "NODE_ARROW_DASH_COUNT"]

    for b in booleans:
        value = config[b]
        config[b] = value.lower() in ("t", "true", "yes", "y")

    for f in floats:
        config[f] = float(config[f])

    for i in integers:
        config[i] = int(config[i])

    config["NODE_MARGIN_BOTTOM"] = clamp(config["NODE_MARGIN_BOTTOM"], 0, 10)
    config["NODE_ARROW_DASH_COUNT"] = clamp(config["NODE_ARROW_DASH_COUNT"], 0, 100)
