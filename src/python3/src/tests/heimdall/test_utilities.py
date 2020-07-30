
from tests.path import CSV_DICTIONARY

import os
import unittest
import os.path

from tests.path import CONTEXT_GUESS_HOMES, G0_MINI_ME_PATH, MOCK_FILES
from tests.temp_file_builder import setup_tmp_git_author_repo

from constants import SCANNER_CONTEXT
from utilities import get_dictionary_list_from_csv
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_text, get_levenshtein_pairs
from utilities.heimdall.path import is_editor_swapfile
from utilities.heimdall.git import scan_git_authors
from utilities import guess_user_home_from_path, pretty
from utilities.path import iterative_deepening_search
from utilities.maestro import get_weird_assignments_from_config_path
from heimdall.file_cache import file_cache


class TestUtilities(unittest.TestCase):

    def test_file_cache(self):
        path = MOCK_FILES+"suites_without_codes/w003/modules/module1/link-to-task1.tsk"
        result = file_cache.is_broken_symlink(path)
        self.assertFalse(result)

        path = MOCK_FILES+"suites_with_codes/e004/modules/main/broken-symlink"
        result = file_cache.is_broken_symlink(path)
        self.assertTrue(result)

    def test_csv_dictionary(self):
        result = get_dictionary_list_from_csv(CSV_DICTIONARY)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["name"], "george")

        self.assertIn("noise", result[0])
        
    def test_iterative_deepening_search(self):
        """
        This test is technically non-deterministic.
        If it fails, consider rerunning the tests, or rewriting 
        the test so it's more stable on all systems.
        """
        self.maxDiff=None
        
        path=MOCK_FILES+"iterative_deepening_search/folder1/"
        max_seconds=0.1
        debug_sleep_seconds=0.04
        result=iterative_deepening_search(path,max_seconds,
                                          debug_sleep_seconds=debug_sleep_seconds)
        expected=[path+"file1a",
                  path+"file1b",
                  path+"folder2/file2a",
                  path+"folder2/file2b"]
        msg="\nresult =\n"+"\n".join(result)
        self.assertEqual(result,expected,msg=msg)

    def test_git_authors(self):
        path = setup_tmp_git_author_repo()
        result = scan_git_authors(path)
        self.assertTrue(result)

        self.assertEqual(result[0]["name"], "Jimbo Jimbo")
        self.assertEqual(result[1]["name"], "Joe Joe")

        emails = result[0]["emails"]
        self.assertEqual(len(emails), 3)

    def test_get_weird_assignments_from_config(self):
        path = MOCK_FILES+"weird-config-semi-xml.cfg"
        result = get_weird_assignments_from_config_path(path)
        expected = {"input": {"anl_archives": "${__archives__}"},
                    "executables": {"editfst": "editfst",
                                    "r.read_link": "r.read_link",
                                    "copy": "${ASSIMCYCLE_TRANSFER_COMMAND}"},
                    "output": {"anlalt_nosfc": "${ASSIMCYCLE_getalt_output}/${ASSIMCYCLE_DATE}_000_nosfc"}
                    }
        self.assertEqual(result, expected)

        path = MOCK_FILES+"weird-config-semi-xml2.cfg"
        result = get_weird_assignments_from_config_path(path)
        self.assertEqual(len(result["input"]), 3)
        self.assertEqual(len(result["executables"]), 14)
        self.assertEqual(len(result["output"]), 0)

    def test_is_editor_swapfile(self):
        swapfiles = ["/folder1/.file1.swp",
                     "/folder1/.file1.swo",
                     "/folder1/#file1#",
                     "/folder1/.#file1"]

        for path in swapfiles:
            self.assertTrue(is_editor_swapfile(path), msg="path = '%s'" % path)

        not_swapfiles = ["/folder1/.file.swf",
                         "/folder1/.file.swp.txt",
                         "/folder1/file.swp",
                         "/folder1/#file1#.txt"]

        for path in not_swapfiles:
            self.assertFalse(is_editor_swapfile(path), msg="path = '%s'" % path)

    def test_guess_user_home_from_path(self):

        def r(path):
            return os.path.realpath(path)+"/"

        path = MOCK_FILES+"homes/smco500/maestro_suites/preop_zdps/"
        expected = r(MOCK_FILES+"homes/smco502/")
        result = guess_user_home_from_path(path)
        self.assertEqual(result, expected)

        "use realpath to explore parent folders for home tests"
        path = MOCK_FILES+"suites_with_codes/w005/"
        expected = r(MOCK_FILES+"homes/smco502/")
        result = guess_user_home_from_path(path)
        self.assertEqual(result, expected)

        path = os.environ["HOME"]+"/this-folder-does-not-exist-probably/123/"
        expected = r(os.environ["HOME"]+"/")
        result = guess_user_home_from_path(path)
        self.assertEqual(result, expected)

    def test_nodelogger_signals(self):

        task_text = """${destination}/${ENVAR_output_banco_name}.postalt.${outputfile}
                    fi
                done
            fi ## Fin du 'else' relie au 'if [ -f ${TASK_INPUT}/${target} ]'
        else
            $SEQ_BIN/nodelogger -n $SEQ_NODE -s infox -m  "Put ${target} in ${destination} (remote copy)"
            ssh ${destination%%:*} mkdir -p ${destination##*:}

 $SEQ_BIN/nodelogger -n $SEQ_NODE -s abort

            if [ "${ENVAR_output_mode}" = tree ]; then
                ssh ${destination%%:*} mkdir -p ${destination##*:}/${ENVAR_output_banco_name}/postalt
            fi
"""
        results = get_nodelogger_signals_from_task_text(task_text)
        signals = [r["signal"] for r in results]
        expected = ["infox", "abort"]
        self.assertEqual(signals, expected)

    def test_context_guess(self):
        paths = {CONTEXT_GUESS_HOMES+"smco500/.suites/zdps": SCANNER_CONTEXT.OPERATIONAL,
                 CONTEXT_GUESS_HOMES+"smco502/.suites/zdps": SCANNER_CONTEXT.OPERATIONAL,
                 CONTEXT_GUESS_HOMES+"smco502/maestro_suites/zdps": SCANNER_CONTEXT.OPERATIONAL,
                 CONTEXT_GUESS_HOMES+"smco502/.suites/preop_zdps": SCANNER_CONTEXT.PREOPERATIONAL,
                 CONTEXT_GUESS_HOMES+"smco501/.suites/zdps": SCANNER_CONTEXT.PARALLEL,
                 CONTEXT_GUESS_HOMES+"smco500/maestro_suites/zdps": SCANNER_CONTEXT.OPERATIONAL,
                 G0_MINI_ME_PATH: SCANNER_CONTEXT.TEST}

        for path, expected in paths.items():
            msg = "\npath = '%s'" % path
            self.assertTrue(os.path.exists(path), msg=msg)
            result = guess_scanner_context_from_path(path)
            self.assertEqual(result, expected, msg=msg)

    def test_get_levenshtein_pairs(self):
        items = ["cat", "ppp1", "ppp2"]
        result = get_levenshtein_pairs(items)
        expected = {"pairs": [["ppp1", "ppp2"]],
                    "no_match": ["cat"],
                    "matches": ["ppp1", "ppp2"]}
        msg = "\nexpected = \n"+pretty(expected)+"\nresult = \n"+pretty(result)
        self.assertEqual(result, expected, msg=msg)
