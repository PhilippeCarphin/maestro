
import jsonschema
from utilities.pretty import pretty_json


def assert_valid_json(j, schema, message=""):
    if not schema:
        raise ValueError("assert_valid_json got an empty schema. This was probably a mistake.")

    "by default, only lists are considered 'array'. Add Python tuple to this."
    jsonschema.validate(j, schema, types={'array': (list, tuple)})


def get_json_validation_error_message(j, schema):
    "return empty string if valid"
    try:
        jsonschema.validate(j, schema)
    except jsonschema.exceptions.ValidationError as e:
        return str(e)
    return ""


def is_valid_json(j, schema):
    try:
        jsonschema.validate(j, schema)
    except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError):
        return False
    return True


def write_pretty_json(path, data):
    with open(path, "w") as f:
        f.write(pretty_json(data))
