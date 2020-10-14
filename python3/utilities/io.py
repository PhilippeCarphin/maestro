
import gzip
import os

from constants import ENCODINGS
from utilities.colors import print_green
from utilities.path import get_matching_paths_recursively

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