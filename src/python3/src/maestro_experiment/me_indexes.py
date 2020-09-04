import os.path
from collections import OrderedDict

from home_logger import logger
from utilities.parsing import superstrip
from utilities.maestro.loop import get_loop_indexes_from_loop_data, get_loop_composite_data_from_xml

"""
This code handles code related to nodes with indexes like:
    <SWITCH>
    <LOOP>
    <NPASS_TASK>
for the MaestroExperiment class.

For loop data structures, see src/maestro/loop.py

This abstract class is not meant to be instantiated, only inherited.
"""


class ME_Indexes():

    def has_indexes(self, node_path):
        return self.is_loop(node_path) or self.is_npass_task(node_path)

    def get_indexes_from_node_path(self, node_path):

        if node_path.endswith("/"):
            node_path = node_path[:-1]

        if self.is_loop(node_path):
            composite = self.get_loop_composite_data(node_path)
            indexes = []
            for loop_data in composite:
                indexes += get_loop_indexes_from_loop_data(**loop_data)
            return indexes
        elif self.is_npass_task(node_path):
            return self.get_indexes_from_npass_task(node_path)
        else:
            return []

    def get_indexes_from_npass_task(self, node_path):
        "if no snapshot/datestamp is set, we cannot lookup npt indexes."
        if not self.long_datestamp:
            return []

        path_prefix = self.path+"sequencing/status/"+self.long_datestamp+"/"+node_path
        node_name = superstrip(node_path, "/ ").split("/")[-1]
        folder = os.path.dirname(path_prefix)

        "no folder means task has not run yet, cannot lookup npt indexes."
        if not os.path.isdir(folder):
            return []

        """
        A filename like:
            pizza2.+0.end
        has just one index, whereas:
            pizza2.+0+p2index1.end
        has two.
        
        The keys for this dictionary is the index count, value is a list of discovered indexes.
        In this example indexes_by_icount[2]=["p2index1", ...]
        This needs to be done to find only the latest indexes using filenames with
        the highest index count.
        """
        indexes_by_icount = {}

        for filename in os.listdir(folder):
            if filename.startswith(node_name):

                """
                Given a filename like:
                    'pizza2.+0+p2index1.end'
                retrieve index:
                    'p2index1'
                """
                chunks = filename.split("+")
                try:
                    index = chunks[-1].split(".")[0]
                except:
                    continue

                icount = len(chunks)-1
                if icount not in indexes_by_icount:
                    indexes_by_icount[icount] = []
                indexes_by_icount[icount].append(index)

        if not indexes_by_icount:
            return []
        highest = max(indexes_by_icount.keys())
        return sorted(indexes_by_icount[highest])

    def get_loop_composite_data(self, node_path):
        "See loop.py for info on loop_composite_data"
        path = self.path+"/resources/"+node_path+"/container.xml"
        root = self.get_interpreted_resource_lxml_element(path)
        return get_loop_composite_data_from_xml(root, logger=logger)

    def get_index_map(self, node_path):
        """
        Suppose node_path = "/main/loop1/task1/loop2/task2/task3"

        loop1 indexes are 2,4,6,8
        loop2 indexes are 1,2,3

        Returns {"loop1":[2,4,6,8],
                 "loop2":[1,2,3]}
        """

        assert type(node_path) is str
        result = OrderedDict()

        chunks = [c for c in node_path.split("/") if c.strip()]
        cursor = ""
        for chunk in chunks:

            if cursor:
                cursor += "/"
            cursor += chunk

            indexes = self.get_indexes_from_node_path(cursor)

            if indexes:
                result[chunk] = indexes
        return result

    def get_first_index_selection(self, node_path):
        """
        For example, for a node_path = "/main/loop1/task1/loop2/task2/task3"

        returns {"loop1":0,"loop2":0}
        """

        m = self.get_index_map(node_path)
        result = OrderedDict()
        for key, value in m.items():
            result[key] = value[0]
        return result
