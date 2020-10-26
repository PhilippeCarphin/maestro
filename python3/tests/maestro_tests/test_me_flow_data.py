import unittest

from tests.cache import TURTLE_ME
from constants import JSON_SCHEMAS, NODE_TYPE
from utilities import assert_valid_json, pretty, pretty_kwargs
from tests.path import NODE_PATHS_G0, NODE_PATHS_G1, NODE_PATHS_COMP_EXP
from tests.cache import G0_MINI_ME, G1_MINI_ME, BIG_ME

"""
Tests for getting information about nodes.
"""

TURTLE_DATESTAMP1 = "2020040100"


class TestMaestroExperimentFlowData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = 2000

    def test_turtle_experiment_flow_data(self):
        node_path = "turtle"
        me = TURTLE_ME
        result = me.get_flow_data(node_path)
        assert_valid_json(result, JSON_SCHEMAS.FLOW)

        children = ["turtle/turtleTask1", "turtle/TurtlePower", "turtle/turtleSlowpoke", "turtle/turtleMemory"]
        submits = children
        flow_branch = "turtle"
        expected = {"flow_children_node_paths": children,
                    "flow_branch": flow_branch,
                    "flow_path": me.path+"modules/turtle/flow.xml",
                    "module_name": "turtle",
                    "module_path_inner": "turtle",
                    "submits_children_node_paths": submits,
                    "type": NODE_TYPE.MODULE}

        msg = pretty_kwargs(result=result, expected=expected)
        self.assertEqual(result, expected, msg=msg)

    def test_g0_submit_families_same_name_two_modules(self):
        "Two modules have 'submit_families' in g0."
        me = G0_MINI_ME

        node_path = "main/pre_assimcycle/cutoff/submit_families"
        node_data = me.get_node_data(node_path)
        result = node_data["flow_branch"]
        expected = "main/pre_assimcycle/get_arcdata_cutoff/cutoff/submit_families"
        self.assertEqual(result, expected)

        node_path = "main/pre_assimcycle/derialt/submit_families"
        node_data = me.get_node_data(node_path)
        result = node_data["flow_branch"]
        expected = "main/pre_assimcycle/get_arcdata_derialt/derialt/submit_families"
        self.assertEqual(result, expected)

    def test_gdps_flow_g0_forecast_module(self):
        """
        There are a couple 'forecast' modules, some empty, in the whole flow.
        Verify that they appear where we expect them to.
        """
        me = G0_MINI_ME

        result = me.root_flow.xpath("//MODULE/MODULE[@name='forecast']")
        self.assertTrue(result, msg=pretty(me.root_flow))

        """
        The test above is more precise, but some bugs cause it to fail non-deterministically.        
        This test is deterministic.
        """
        xml = pretty(me.root_flow)
        search = "<MODULE name=\"forecast\""
        self.assertEqual(xml.count(search), 2)

    def test_gdps_flow_g0_g1(self):

        trials = ((G0_MINI_ME, NODE_PATHS_G0),
                  (G1_MINI_ME, NODE_PATHS_G1),
                  (BIG_ME, NODE_PATHS_COMP_EXP))

        for me, expected_paths in trials:
            results = sorted(me.get_node_paths(), key=len)

            msg = "\n\nexperiment = '%s'" % me.name
            for result in results:
                if me.node_path_contains_switch(result):
                    "skip switches, because in xflow/nodeinfo/tsvinfo their paths are twisted and do not follow the XML structure"
                    continue
                self.assertIn(result, expected_paths, msg=msg)

            for expected in expected_paths:
                if me.node_path_contains_switch(expected):
                    "skip switches, because in xflow/nodeinfo/tsvinfo their paths are twisted and do not follow the XML structure"
                    continue
                self.assertIn(expected, results, msg=msg)
