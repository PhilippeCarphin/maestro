import os
import time
import signal
from constants import *
import subprocess
import psutil

try:
    from subprocess import check_output, CalledProcessError, Popen
except ImportError:
    def check_output(cmd):
        return subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()

def get_matching_paths_recursively(rootdir, extension, verbose=0):
    "Returns a list of full paths. Searches 'rootdir' recursively for all files with 'extension'."
    if verbose:
        print("Getting filenames for files with extension \"%s\" at:\n%s" %
              (extension, rootdir))
    results = []
    for root, _, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.find(extension) == len(filename) - len(extension):
                path = os.path.join(root, filename)
                results.append(path)
    return results

def kill_proc_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
    except psutil._exceptions.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)

def is_success_after_x_seconds(cmd,seconds):
    """
    returns true if this command returns a success status after running for this many seconds.
    useful to verify if gui scripts crash soon after launch.
    """
    dv=subprocess.DEVNULL
    process=subprocess.Popen(cmd,shell=True, stdout=dv, stderr=dv)
    time.sleep(seconds)
    poll=process.poll()
    kill_proc_tree(process.pid)
    return not poll

def get_output(cmd, seconds=1):
    try:
        output=check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8")
        return output,0
    except CalledProcessError as e:
        return (e.output.decode("utf8"),e.returncode)
    
    
