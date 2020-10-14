import os
import os.path

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


def insert_into_dictionary(a, b):
    """
    If a key in dictionary 'b' is not in 'a', insert its key/value into 'a'.
    """
    for key, item in b.items():
        if key not in a:
            a[key] = b[key]


