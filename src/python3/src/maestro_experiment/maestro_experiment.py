#!../venv/bin/python3

"""
This class parses a maestro experiment and builds information about it.

This class, and the classes it inherits from, have no code specific to 
any project like for mflow. Instead it only has generally useful 
information about a maestro experiment.
"""

import os
from os import stat
from pwd import getpwuid

from utilities.heimdall.critical_errors import has_critical_error
from utilities.maestro import find_exp_home_in_path, get_experiment_name, get_sequencer_command
from utilities import pretty, clamp
from utilities.xml import xml_cache

from maestro_experiment.me_flow import ME_Flow
from maestro_experiment.me_indexes import ME_Indexes
from maestro_experiment.me_logs import ME_Logs
from maestro_experiment.me_node_data import ME_NodeData
from maestro_experiment.me_node_status import ME_NodeStatus
from maestro_experiment.me_resources import ME_Resources
from maestro_experiment.me_snapshot import ME_Snapshot
from maestro_experiment.me_validation import ME_Validation


class MaestroExperiment(ME_Flow, ME_Indexes, ME_Logs, ME_NodeData, ME_NodeStatus, ME_Resources, ME_Snapshot, ME_Validation):
    def __init__(self,
                 path,
                 datestamp=None,
                 node_log_refresh_interval=10,
                 user_home=None):

        path = find_exp_home_in_path(path)
        if not path or has_critical_error(path):
            raise ValueError("MaestroExperiment failed to find an experiment for path: '%s'" % path)

        """
        A list of strings describing any errors in parsing or reading this experiment path.
        """
        self.validation_errors = []

        """
        key is resource variable like FRONTEND, value is its value from resource files.
        """
        self.resource_cache = {}
        
        """
        A list of all paths to resources.def like files, starting with the highest priority.
        """
        self.resource_definition_paths = []

        """
        key is path to a resoure file like resources.def
        value is the declare dictionary, like:
            {"FRONTEND":"eccc-ppp1"}
        """
        self.path_to_resource_declares = {}

        """
        key is path to a resource XML file, value is a list of variables used there
        which are not defined in the project.
        """
        self.undefined_resource_variables = {}

        """
        key is path to a resource XML file
        value is the lxml element, where its attributes like machine=${ABC} are interpreted.
        """
        self.interpreted_resource_lxml_cache = {}

        self.path = path
        self.name = get_experiment_name(path)

        """
        If this value is set outside this class, maestro can give additional 
        info and warnings if the user cannot submit to a queue.
        MaestroExperiment doesn't find this itself since that may be slow and
        in many cases it is not used.
        """
        self.qstat_data = None

        if user_home:
            self.user_home = user_home
        else:
            self.find_user_home()

        self.inspect_flow()

        """
        Avoid a situation where a user preference requests a full refresh on all
        statuses every 0.01 seconds for very large suites.
        Minimum interval is according to a square root function of node count.
        """
        node_count = len(self.node_datas)
        min_interval = 1+node_count**(1/2)/10
        self.node_log_refresh_interval = clamp(node_log_refresh_interval, min_interval, 600)

        if datestamp:
            self.set_snapshot(datestamp)
        else:
            self.datestamp = ""
            self.long_datestamp = ""

        """
        Build all node datas for the first time, which also builds indexes
        like resource file parsing results.
        """
        self.get_node_datas()

    def get_support_status(self):
        """
        Open ExpOptions.xml and return the status attribute in <SupportInfo>
        """
        xml_path = self.path+"ExpOptions.xml"
        root = xml_cache.get(xml_path)
        if root is None:
            return ""

        support_infos = root.xpath("//SupportInfo")
        if not support_infos:
            return ""

        support_info = support_infos[0]
        return support_info.attrib.get("status", "")

    def has_critical_error(self):
        return has_critical_error(self.path)

    def find_user_home(self):
        "Set home to the home of the owner of the experiment."
        if self.path:
            username = getpwuid(stat(self.path).st_uid).pw_name
            home_root = os.path.dirname(os.environ["HOME"])
            self.user_home = home_root+"/"+username+"/"
        else:
            self.user_home = ""

    def get_workdir_path(self, node_path):
        if not self.long_datestamp:
            return ""

        node_data = self.get_node_data(node_path)
        machine = node_data["machine"]

        path = self.path+"hub/%s/work/%s/" % (machine, self.long_datestamp)
        path += node_path+"/"
        return path

    def get_sequencer_command(self, node_path, signal, **kwargs):
        return get_sequencer_command(self.path,
                                     self.long_datestamp,
                                     node_path,
                                     signal,
                                     **kwargs)

    def __str__(self):
        lines = ["<MaestroExperiment>"]
        lines.append("\npath = '%s'" % self.path)
        lines.append("\nnode_datas = "+pretty(self.node_datas))
        lines.append("\nmodule_name_to_tree = "+pretty(self.module_name_to_tree))
        lines.append("</MaestroExperiment>")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    print(MaestroExperiment(path))
