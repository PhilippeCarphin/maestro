import subprocess
import os
import shlex

def run_shell_cmd(cmd):
    """
    Run this command in a shell and ignore all output and errors.
    Useful to launch gvim.
    """
    subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)

def safe_check_output(cmd):
    "subprocess.check_output can raise an exception. This always returns shell output string."
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf8")

def safe_check_output_with_status(cmd):
    "like safe_check_output, but also returns exit status"
    try:
        status=0
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode("utf8"),status
    except subprocess.CalledProcessError as e:
        status=1
        return e.output.decode("utf8"),status

def get_true_host():
    """
    Returns the first which has a value: $TRUE_HOST, $(hostname), $HOST
    """
    
    host=os.environ.get("TRUE_HOST")
    if host:
        return host.strip()
    
    host,status=safe_check_output_with_status("hostname")
    if host and status==0:
        return host.strip()
    
    host=os.environ.get("HOST")
    if host:
        return host.strip()
    
    return "unknown-hostname"
    