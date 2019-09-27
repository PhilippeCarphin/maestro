import os
import time
import signal
from constants import *
import subprocess

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

def get_output(cmd, seconds=1, use_popen = False):
    
    if use_popen:
        FNULL = open(os.devnull,'w')    
        process = Popen(cmd,shell=True,stdout = FNULL, stdin = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
        time.sleep(seconds)
        return_code = process.poll()
        os.killpg(os.getpgid(process.pid),signal.SIGTERM)
        return (process.stderr.read().decode("utf-8"),return_code)
    else:
        try:
            return (check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8"),0)
        except CalledProcessError as e:
            return (e.output.decode("utf8"),e.returncode)
    
    
