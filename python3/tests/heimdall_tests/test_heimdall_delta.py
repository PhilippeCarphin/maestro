
import unittest
import shutil
import os.path

from utilities.shell import safe_check_output_with_status
from heimdall import get_new_messages_for_experiment_paths
from tests.mock_file_builder import setup_repo_for_delta
from tests.path import TMP_FOLDER, OPERATIONAL_HOME, PARALLEL_HOME, OPERATIONAL_SUITES_HOME

class TestHeimdallDelta(unittest.TestCase):

    def test_old_new_experiment(self):
        path,commit1,commit2=setup_repo_for_delta()
        
        paths=[path]
        scan_history_folder=TMP_FOLDER+"/delta-scan-history/"
        if os.path.exists(scan_history_folder):
            shutil.rmtree(scan_history_folder)

        """
        This loop runs the first and ignores result.
        The second 'result' is kept for after loop check.
        """
        for commit in (commit1,commit2):
            cmd="cd %s && git checkout %s"%(path,commit)
            output,status=safe_check_output_with_status(cmd)
            self.assertEqual(status,0,msg=cmd)
            
            result=get_new_messages_for_experiment_paths(paths,
                                                     scan_history_folder,
                                                     operational_home=OPERATIONAL_HOME,
                                                     parallel_home=PARALLEL_HOME,
                                                     operational_suites_home=OPERATIONAL_SUITES_HOME)
            
        messages=result[path]
        self.assertEqual(len(messages),1)