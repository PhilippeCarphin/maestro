"""
The contents of this script are generally useful and can be copied, without modification, to other python projects.
"""

import re
import os
import gzip
import os.path
from constants import ENCODINGS
from utilities.colors import print_green
from utilities.path import get_matching_paths_recursively


def get_change_time(path):
    try:
        return os.path.getctime(path)
    except FileNotFoundError:
        return "<FileNotFoundError>"
    except PermissionError:
        return "<PermissionError>"
    except OSError:
        "this may occur because of infinitely nested soft links"
        return "<OSError>"


def cache(function):
    """
    later versions of Python have 'functools.cache'
    """
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


def strip_comments_from_text(text):
    """
    Return the text content of this string, minus any lines that are
    comments, like '#' in bash.
    """
    lines = text.split("\n")
    lines = [i for i in lines if not i.strip().startswith("#")]
    return "\n".join(lines)


def insert_into_dictionary(a, b):
    """
    If a key in dictionary 'b' is not in 'a', insert its key/value into 'a'.
    """
    for key, item in b.items():
        if key not in a:
            a[key] = b[key]


def get_distance(x1, x2, y1, y2):
    "returns float cartesian distance between two points"
    x = abs(x1-x2)
    y = abs(y1-y2)
    return (x**2+y**2)**0.5


def get_key_values_from_path(path, include_export_lines=True):

    if not os.path.isfile(path):
        return {}

    text = safe_read(path)

    return get_key_values_from_text(text, include_export_lines)


def get_key_values_from_text(text, include_export_lines=True):
    """
    Given text with bash-like variable declares:
stab        ABC=123
        export DEF=456
    returns:
        {"ABC":"123",
         "DEF":"456"}

    Ignore export lines if include_export_lines is false.
    """

    lines = text.split("\n")

    "select only var declare lines"
    if include_export_lines:
        var_regex = re.compile("(export )?[a-zA-Z]+[a-zA-Z0-9_]*[ ]*=")
    else:
        var_regex = re.compile("[a-zA-Z]+[a-zA-Z0-9_]*[ ]*=")

    lines = [line.strip() for line in lines if var_regex.search(line)]

    data = {}
    for line in lines:
        name = line.split("=")[0]
        if include_export_lines and name.startswith("export "):
            name = name[7:]
        value = line[line.index("=")+1:]
        data[name.strip()] = value.strip()
    return data


def get_key_value_from_path(key, path):
    """
    If key is 'ABC' and file at path contains "ABC=123" returns "123".
    """
    if not os.path.isfile(path):
        return ""
    with open(path, "r") as f:
        return get_key_value_from_text(key, f.read())


def get_key_value_from_text(key, text):
    """
    If key is 'ABC' and text contains "ABC=123" returns "123".
    """
    lines = text.split("\n")
    for line in lines:
        if line.strip().startswith(key) and "=" in line:
            return line.split("=")[-1].strip()
    return ""


def recursive_replace_in_files(before, after, folder):
    "replaces all instances of 'before' with 'after', in all files found in path, recursively"
    if not os.path.isdir(folder):
        return
    for path in get_matching_paths_recursively(folder):
        try:
            with open(path, "r") as f:
                data = f.read()
            data = data.replace(before, after)
            with open(path, "w") as f:
                f.write(data)
        except (UnicodeDecodeError, FileNotFoundError, OSError):
            pass


def get_variable_value_from_file(path, name):
    """
    If name is "FRONTEND"
    finds the first line like "FRONTEND=123" and returns "123"
    """

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except:
        lines = []

    for line in lines:
        if line.startswith(name+"="):
            return line[line.index("=")+1:].strip()

    return ""


def superstrip(text, chars):
    """
    Like Python strip, except uses the characters in the
    list/string 'chars' instead of just whitespace.
    """
    start_index = 0
    end_index = len(text)-1
    for i, c in enumerate(text):
        if c not in chars:
            start_index = i
            break
    for i, c in enumerate(reversed(text)):
        if c not in chars:
            end_index = len(text)-i
            break

    return text[start_index:end_index]


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def safe_get_lines(path):
    """
    Opens plaintext or gzipped files, trying to handle weird encoding gracefully.
    Get all lines from a file which can be decoded. Ideally, all of them.
    This function should never raise an exception - instead add exception handling for specific exceptions as they pop up.
    """

    if is_gzipped(path):
        read_mode = "rt"
        open_function = gzip.open
    else:
        read_mode = "r"
        open_function = open

    encodings = ("utf-8", "latin-1")
    for encoding in encodings:
        try:
            with open_function(path, read_mode, encoding=encoding, errors="ignore") as f:
                return f.readlines()
        except UnicodeDecodeError:
            pass

    return []


def safe_open(path, verbose=False):
    """
    Try multiple encodings, if necessary.
    Do not raise exceptions, return "" if total failure.
    """

    if not os.path.isfile(path):
        return ""

    for encoding in ENCODINGS:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except:
            pass
    return ""


safe_read = safe_open


def safe_write(path, data, verbose=True):
    "Writes this data to path, creates any necessary folders."
    directory = os.sep.join(path.split(os.sep)[:-1])
    if directory and not os.path.exists(directory):
        if verbose:
            print_green("Making directory: '%s'" % directory)
        os.makedirs(directory)
    with open(path, "w") as f:
        f.write(data)
    if verbose:
        print_green("Wrote data to file '%s'" % path)


def is_gzipped(path):
    """
    Returns true if gzipped.
    Unfortunately this slow method may be the only reliable one.
    """
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            f.read()
            return True
    except:
        return False
