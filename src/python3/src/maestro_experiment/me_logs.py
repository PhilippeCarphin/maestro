
"""
This code handles log/listing path and parsing functions for the MaestroExperiment class.

This abstract class is not meant to be instantiated, only inherited.
"""

from collections import OrderedDict


class ME_Logs():

    def get_latest_abort_log(self, node_path, loop_indexes_selected=None):
        return self.get_latest_log(node_path, "abort", loop_indexes_selected=loop_indexes_selected)

    def get_latest_success_log(self, node_path, loop_indexes_selected=None):
        return self.get_latest_log(node_path, "success", loop_indexes_selected=loop_indexes_selected)

    def get_latest_submission_log(self, node_path, loop_indexes_selected=None):
        return self.get_latest_log(node_path, "submission", loop_indexes_selected=loop_indexes_selected)

    def get_latest_log(self, node_path, log_type, loop_indexes_selected=None):

        assert log_type in ("abort", "success", "submission")
        assert type(loop_indexes_selected) in (dict, OrderedDict, type(None))

        node_data = self.get_node_data(node_path)

        log_path = self.path+"listings/latest/"

        log_path += node_path

        "if no loop indexes, use default first, for example [0,0]"
        first_selection = self.get_first_index_selection(node_path)
        first_indexes = [index for index in first_selection.values()]
        if not loop_indexes_selected:
            loop_indexes_selected = first_selection
        indexes = [index for index in loop_indexes_selected.values()]

        "if not enough loop indexes are chosen, append the defaults. for example [3] becomes [3,0]"
        if len(indexes) < len(first_indexes):
            indexes += first_indexes[len(indexes):]

        if indexes:
            log_path += ".+"+"+".join([str(i) for i in indexes])

        log_path += "."+self.datestamp+"0000"

        log_path += "."+log_type

        log_path += "@"+node_data["machine"]

        return log_path
