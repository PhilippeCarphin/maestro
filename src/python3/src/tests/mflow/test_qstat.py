
import unittest

from utilities import get_qstat_data_from_path
from tests.path import QSTAT_OUTPUT1_PATH


class TestQstat(unittest.TestCase):

    def test_qstat_parsing(self):
        data = get_qstat_data_from_path(QSTAT_OUTPUT1_PATH)

        result = data["prod"]["acl_users"]
        expected = sorted("jam007,smco500,smco501,smco600,smco601".split(","))
        self.assertEqual(result, expected)

        "production == prod"
        result = data["production"]["acl_users"]
        self.assertEqual(result, expected)

        result = sorted(list(data.keys()))
        expected = sorted(["prod", "prod_xxfer", "dev", "development",
                           "prod_daemon", "production", "prod_hpnls",
                           "archive", "hpnls", "project", "dev_xxfer",
                           "dev_daemon", "dedicated_bench", "ibmbench",
                           "prod_persistent", "prod_p", "crayadm"])
        self.assertEqual(result, expected)

        result = data["development"]["acl_users"]
        self.assertEqual(result, [])
