
from tests.path import CSV_DICTIONARY

import os
import unittest
import os.path

from tests.path import CONTEXT_GUESS_HOMES, G0_MINI_ME_PATH, MOCK_FILES, SUITES_WITHOUT_CODES, ABSOLUTE_SYMLINK_EXISTS_PATH, TURTLE_ME_PATH
from tests.test_file_builder import setup_tmp_git_author_repo, setup_tricky_mock_files

from constants import SCANNER_CONTEXT
from utilities import get_dictionary_list_from_csv
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_text, get_levenshtein_pairs, get_constant_definition_count, get_ssm_domains_from_string, get_etiket_variables_used_from_path
from utilities.heimdall.path import is_editor_swapfile, get_latest_ssm_path_from_path
from utilities.heimdall.git import scan_git_authors
from utilities import guess_user_home_from_path, pretty, pretty_kwargs
from utilities.path import iterative_deepening_search, get_link_chain_from_link
from utilities.maestro import get_weird_assignments_from_config_path, get_commented_pseudo_xml_lines
from utilities.parsing import get_bash_variables_used_in_text
from heimdall.file_cache import file_cache


class TestUtilities(unittest.TestCase):
    
    def test_used_bash_variables(self):
        text="""
        
        ABC=123
        echo $CAT ${DOG}
        # echo $TURTLE
        """
        result=get_bash_variables_used_in_text(text)
        expected=["CAT","DOG"]
        self.assertEqual(result,expected)
    
    def test_find_etiket(self):
        path = MOCK_FILES+"suites_with_codes/e005/modules/module1/task1.tsk"
        result=get_etiket_variables_used_from_path(path)
        expected=["CMCGANAETIK",
                  "CMCRDPSETIK",
                  "ETIK",
                  "E_TIKET_DEFINED_IN_BAD_PLACE_ETIK"]
        self.assertEqual(result,expected)
        
        path = MOCK_FILES+"suites_with_codes/e005/experiment.cfg"
        result=get_etiket_variables_used_from_path(path,require_etiket_programs=True)
        self.assertFalse(result)
    
    def test_link_chain(self):
        expected=[MOCK_FILES+"link-chain/link4",
                  MOCK_FILES+"link-chain/folder1",
                  MOCK_FILES+"link-chain/folder1/link3",
                  MOCK_FILES+"link-chain/link2",
                  MOCK_FILES+"link-chain/link1",
                  MOCK_FILES+"link-chain/link-chain-target"]
        start=expected[0]
        result=get_link_chain_from_link(start)
        msg=pretty_kwargs(expected=expected,result=result)
        self.assertEqual(expected,result,msg=msg)

    def test_file_cache(self):
        path = MOCK_FILES+"suites_without_codes/w003/modules/module1/link-to-loop1.tsk"
        result = file_cache.is_broken_symlink(path)
        self.assertFalse(result)

        path = MOCK_FILES+"suites_with_codes/e004/modules/main/broken-symlink"
        result = file_cache.is_broken_symlink(path)
        self.assertTrue(result)
        
        setup_tricky_mock_files()
        result = file_cache.is_broken_symlink(ABSOLUTE_SYMLINK_EXISTS_PATH)
        self.assertFalse(result)
        
        not_broken=("folder1","link-to-folder1",
                    "file1","link-to-file1")
        for basename in not_broken:
            path = MOCK_FILES+"symlinks/"+basename
            self.assertTrue(os.path.exists(path))
            result = file_cache.is_broken_symlink(path)
            self.assertFalse(result)
            
    def test_latest_ssm_version(self):
        folder=MOCK_FILES+"ssm-versions/"
        
        path=folder+"1.5"
        result=get_latest_ssm_path_from_path(path)
        self.assertEqual(result,"1.7")
        
        path=folder+"1.5"
        result=get_latest_ssm_path_from_path(path,include_betas=True)
        self.assertEqual(result,"1.7-beta")
        
        path=folder+"1.5.5"
        result=get_latest_ssm_path_from_path(path)
        self.assertEqual(result,"1.6.2")
        
    def test_get_ssm_domains_from_string(self):
        line=". ssmuse-sh -d abc -d def"
        result=get_ssm_domains_from_string(line)
        expected=["abc","def"]
        self.assertEqual(result,expected)
        
        line=". ssmuse-sh -x abc"
        result=get_ssm_domains_from_string(line)
        expected=["abc"]
        self.assertEqual(result,expected)
        
        line="  . r.load.dot abc def"
        result=get_ssm_domains_from_string(line)
        expected=["abc","def"]
        self.assertEqual(result,expected)
        
        line="#  . r.load.dot abc def"
        result=get_ssm_domains_from_string(line)
        self.assertFalse(result)
        
        line="   echo 123 | grep 123"
        result=get_ssm_domains_from_string(line)
        self.assertFalse(result)
        
    def test_get_commented_pseudo_xml_lines(self):
        path=SUITES_WITHOUT_CODES+"b007/modules/module1/task1.cfg"
        with open(path,"r") as f:
            content=f.read()
        lines=get_commented_pseudo_xml_lines(content)
        self.assertFalse(lines)
        
    def test_get_constant_definition_count(self):
        text="""
ABC=123
ABC=456
        
   CAT=123
        
# CAT=123
echo 123 = 123"""
        expected={"ABC":2,"CAT":1}
        result=get_constant_definition_count(text)
        self.assertEqual(result,expected)

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
        max_seconds=0.2
        debug_sleep_seconds=0.04
        result=iterative_deepening_search(path,max_seconds,
                                          debug_sleep_seconds=debug_sleep_seconds)
        expected=[path+"file1a",
                  path+"file1b",
                  path+"folder2/file2a",
                  path+"folder2/file2b"]
        msg=pretty_kwargs(result=result,expected=expected)
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
