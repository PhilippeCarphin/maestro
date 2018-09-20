
import json, os.path, sys
import time, subprocess

from utilities.colors import *


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)

def show_duration(label, start_time, print_function=None):
    "Compares start_time to current time and prints a short report."
    duration = time.time() - start_time
    if not print_function:
        if duration < 0.05:
            print_function = print_green
        elif duration < 0.2:
            print_function = print_yellow
        else:
            print_function = print_red
    print(label)
    print_function("       %.3f seconds" % duration)


def write_pretty_json(path, data):
    pretty=json.dumps(data,indent=4,sort_keys=True)
    with open(path, "w") as f:
        f.write(pretty)

def get_git_repo_version():
    "attempts 'git describe', if that fails returns the HEAD commit hash, or 'unknown'."
    cwd=os.path.dirname(os.path.realpath(sys.argv[0]))
    try:
        return subprocess.check_output("git describe 2>/dev/null",cwd=cwd,shell=True).decode("utf8")
    except:
        pass
    
    try:
        return "commit "+subprocess.check_output("git rev-parse HEAD 2>/dev/null",cwd=cwd,shell=True).decode("utf8")[:16]
    except:
        return "unknown"

def get_bytes_size_from_bytes_string(text):
    "Given a string like '12k', returns 12000. Works with KMGT. Case insensitive."
    if not text:
        return 0
    text=text.strip()
    if not text:
        return 0
    
    suffixes={"k":1000,"m":10**6,"g":10**9,"t":10**12}
    multiplier=suffixes.get(text[-1].lower(),1)
    
    return float(text[:-1].strip())*multiplier

def safe_check_output(cmd):
    "subprocess.check_output can raise an exception. This always returns shell output string."
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf8")