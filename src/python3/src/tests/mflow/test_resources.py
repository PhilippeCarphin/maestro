
import unittest

from utilities import get_key_value_from_path, get_key_values_from_path, get_true_host
from tests.path import RESOURCES_HOME1, RESOURCES_HOME2, TURTLE_ME_PATH
from tests.cache import STRANGE_RESOURCES_ME
from constants import DEFAULT_BATCH_RESOURCES
from maestro_experiment import MaestroExperiment

"""
Tests for finding and parsing resource DEF and XML files.
    overrides.def
    default_resources.def
    resources/resources.def
    
    resources/../turtleTask1.xml
"""

TURTLE_DATESTAMP1 = "2020040100"


class TestMaestroResources(unittest.TestCase):

    def test_get_resource_value(self):
        path = RESOURCES_HOME1+".suites/default_resources.def"
        result = get_key_value_from_path("FRONTEND", path)
        expected = "frontend-def-res-home1"
        self.assertEqual(result, expected)

        result = get_key_values_from_path(path)
        expected = "frontend-def-res-home1"
        self.assertEqual(result["FRONTEND"], expected)

    def test_me_get_resource_value(self):
        me = MaestroExperiment(TURTLE_ME_PATH, user_home=RESOURCES_HOME1)

        "ignore default_resources.def because task resource xml exists"
        result = me.get_resource_value_from_key("FRONTEND")
        expected = "turtle-frontend"
        self.assertEqual(result, expected)

        result = me.get_resource_value_from_key("SEQ_DEFAULT_MACHINE")
        expected = "turtle-default-machine"
        self.assertEqual(result, expected)

        "ignore task resource xml because overrides.def exists"
        me = MaestroExperiment(TURTLE_ME_PATH, user_home=RESOURCES_HOME2)
        result = me.get_resource_value_from_key("FRONTEND")
        expected = "overrides-home2-frontend"
        self.assertEqual(result, expected)

        result = me.get_resource_value_from_key("SEQ_DEFAULT_MACHINE")
        expected = "overrides-home2-default-machine"
        self.assertEqual(result, expected)

    def test_me_node_data_resources(self):
        "values in node_data that are obtained from the XML files in 'resources' "

        "empty XML, default resources"
        path = "/home/that/does/not/exist/"
        me = MaestroExperiment(TURTLE_ME_PATH, user_home=path)
        node_path = "turtle/turtleTask2"
        result_node_data = me.get_node_data(node_path)
        "defaults presently found in SeqNode.c around line 680"

        for key, expected in DEFAULT_BATCH_RESOURCES.items():
            self.assertIn(key, result_node_data)
            result = result_node_data[key]
            self.assertEqual(result, expected)

        "use resources file and xml file to figure out custom value"
        me = MaestroExperiment(TURTLE_ME_PATH, user_home=RESOURCES_HOME2)
        node_path = "turtle/turtleTask1"
        result_node_data = me.get_node_data(node_path)
        machine = "overrides-home2-default-machine"
        expected = machine
        result = result_node_data["machine"]
        self.assertEqual(result, expected)

        "correct machine is appended to log path"
        result = me.get_latest_success_log(node_path)
        self.assertTrue(result.endswith("@"+machine))

    def test_undefined_resource_variables(self):
        me = STRANGE_RESOURCES_ME
        xml_path = me.path+"resources/module1/task1.xml"
        self.assertIn(xml_path, me.undefined_resource_variables)
        result = me.undefined_resource_variables[xml_path]
        self.assertEqual(len(result), 1, msg="result = "+str(result))
        self.assertEqual(result[0], "NOT_DEFINED")

    def test_resource_variable_insert(self):
        """
        Sometimes we see multiple inserts like:
            machine="${ABC}x${ABC}"
        """

        me = STRANGE_RESOURCES_ME
        xml_path = me.path+"resources/module1/task1.xml"
        data = me.get_batch_data_from_xml(xml_path)
        self.assertEqual(data.get("machine"), "123x123", msg="\ndata = "+str(data))
