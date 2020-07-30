import os.path

from utilities import clamp
from utilities.shell import safe_check_output_with_status


def get_qstat_data_from_path(path):
    if not os.path.isfile(path):
        return {}
    with open(path, "r") as f:
        return get_qstat_data_from_text(f.read())


def get_resource_limits_from_qstat_data(qstat_data, queue):
    """
    Attempt to parse qstat values from qstat_data to return a dictionary
    of walltime, cpu, memory
    """

    walltime = 0
    cpu = 0
    memory = 0

    try:
        text = qstat_data[queue]["resources_max.walltime"]
        h, m, s = text.strip().split(":")
        h = int(h)
        m = int(m)
        s = int(s)
        assert h >= 0 and m >= 0 and s >= 0
        walltime = h*3600+m*60+s
    except:
        pass

    try:
        cpu = int(qstat_data[queue]["resources_max.ncpus"])
    except:
        pass

    try:
        text = qstat_data[queue]["resources_max.mem"]
        memory = int(text[:-2])
        if text.lower().endswith("tb"):
            memory *= 1024**4
        if text.lower().endswith("gb"):
            memory *= 1024**3
        if text.lower().endswith("mb"):
            memory *= 1024**2
        if text.lower().endswith("kb"):
            memory *= 1024
    except:
        pass

    return {"wallclock_seconds": walltime,
            "cpu_count": cpu,
            "memory_bytes": memory}


def get_qstat_data_from_text(text):
    """
    Returns a dictionary of parsing the content from command:
        jobctl-qstat -Q -f 

    dictionary:
        {
            "production":{"acl_users":["smco500", ...],
                          "enabled": "True",
                          ...}
            "prod_persistent": ...
        }
    """
    lines = text.strip().split("\n")

    data = {}
    queue = ""
    for line in lines:

        if line.startswith("Queue: "):
            queue = line[7:].strip()
            if queue not in data:
                data[queue] = {}
            continue

        if not queue:
            continue

        if " = " in line:
            split = line.strip().split(" = ")
            if len(split) != 2:
                continue
            key, value = split

            if key == "acl_users":
                value = sorted(value.split(","))

            data[queue][key] = value

    apply_qstat_routes_to_qstat_data(data)

    return data


def get_qstat_data(logger=None, timeout=0):
    """
    Run a full qstat command and return a dictionary with its parsed data.
    If non-zero, timeout is how long in seconds until giving up.
    """

    cmd = "jobctl-qstat -Q -f"

    if timeout and type(timeout) is int:
        timeout = clamp(timeout, 1, 60)
        cmd = "timeout %s %s" % (timeout, cmd)

    output, status = safe_check_output_with_status(cmd)

    if status != 0:
        if logger:
            msg = "qstat command '%s' failed. output:" % cmd
            msg += output
            if len(msg) > 1000:
                msg = msg[:1000]+" ..."
            logger.error(msg)
        return None

    try:
        return get_qstat_data_from_text(output)
    except:
        pass

    return None


def apply_qstat_routes_to_qstat_data(qstat_data):
    """
    A qstat route is like a soft link.
    Sometimes a queue is missing data and instead has a "route" alias where
    more of its data can be found.

    This takes the link target route data and applies it to the link source,
    if necessary.

    Some queues like 'production' don't directly have 'acl_users'
    instead they have something like 'route_destinations = prod'
    So this also applies 'acl_users' from 'prod' to 'production'
    """

    for queue, queue_data in qstat_data.items():

        target_name = queue_data.get("route_destinations")
        if not target_name:
            continue

        target_data = qstat_data.get(target_name)
        if not target_data:
            continue

        if "acl_users" in queue_data:
            continue
        queue_data["acl_users"] = target_data.get("acl_users", [])

        "If source is missing any data, copy it from its target"
        for key in target_data:
            if key not in queue_data:
                queue_data[key] = target_data[key]
