import unittest

from tests.cache import get_experiment_from_cache
from tests.path import SUITES_WITH_CODES
from utilities.pretty import pretty_kwargs
from maestro_experiment.me_dependencies import new_dep_data, resolve_dependency_path

class TestMaestroExperimentDependencies(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = 2000
        
    def test_resolve_dependency_path(self):
        
        node_path="/module1/loop1"
        result=resolve_dependency_path("/module1/task1",node_path)
        expected="/module1/task1"
        self.assertEqual(result,expected)
        
        node_path="/module1/loop1"
        result=resolve_dependency_path("./task2",node_path)
        expected="/module1/task2"
        self.assertEqual(result,expected)
        
        node_path="/module1/loop1/loop2"
        result=resolve_dependency_path("../task3",node_path)
        expected="/module1/task3"
        self.assertEqual(result,expected)

    def test_get_dep_data(self):
        path=SUITES_WITH_CODES+"b007"
        me = get_experiment_from_cache(path)
        node_path="module1/task1/task2/task3"
        result = me.get_dependency_data_for_node_path(node_path)
        expected=[new_dep_data(node_path="/module1/task1",dep_name="/module1/task1"),
                  new_dep_data(node_path="/module1/task1/task2",dep_name="../task2"),
                  new_dep_data(node_path="/turtle/TurtlePower/pizza1",
                               experiment_path="/path/does/not/exist",
                               dep_name="/turtle/TurtlePower/pizza1")]
        msg=pretty_kwargs(result=result,expected=expected)
        self.assertEqual(result,expected,msg)
