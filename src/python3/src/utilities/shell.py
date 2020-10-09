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
        output_bytes=subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output_bytes=e.output

    return safe_decode(output_bytes)

def safe_decode(bytes_to_decode,default=""):
    """
    Tries to decode these bytes with various encodings, returns the default if all fails.
    """

    for encoding in ("iso-8859-1","utf-8"):
        try:
            return bytes_to_decode.decode(encoding)
        except:
            pass

    return default

def safe_check_output_with_status(cmd):
    "like safe_check_output, but also returns exit status"
    try:
        status = 0
        output_bytes=subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        status = 1
        output_bytes=e.output

    return safe_decode(output_bytes), status

def get_true_host():
    """
    Returns the first which has a value: $TRUE_HOST, $(hostname), $HOST
    """

    host = os.environ.get("TRUE_HOST")
    if host:
        return host.strip()

    host, status = safe_check_output_with_status("hostname")
    if host and status == 0:
        return host.strip()

    host = os.environ.get("HOST")
    if host:
        return host.strip()

    return "unknown-hostname"
