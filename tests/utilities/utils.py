import os
import time
import signal
import subprocess
from constants import *
from subprocess import check_output, CalledProcessError, Popen

def get_output(cmd, use_popen = False):
    
    if use_popen:
        FNULL = open(os.devnull,'w')    
        process = Popen(cmd,shell=True,stdout = FNULL, stdin = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn=os.setsid)
        time.sleep(1)
        os.killpg(os.getpgid(process.pid),signal.SIGTERM)
        time.sleep(1)
        errorcode = process.poll()
        return (process.stderr.read().decode("utf-8"),errorcode)
    else:
        try:
            return (check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8"),0)
        except CalledProcessError as e:
            return (e.output.decode("utf8"),e.returncode)
    
    