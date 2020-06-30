
from tests.path import CSV_DICTIONARY

import os
import unittest
import os.path

from tests.path import CONTEXT_GUESS_HOMES, G0_MINI_ME_PATH, MOCK_FILES
from constants import SCANNER_CONTEXT
from utilities import get_dictionary_list_from_csv
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_text
from utilities import guess_user_home_from_path

class TestUtilities(unittest.TestCase):
            
    def test_csv_dictionary(self):
        result=get_dictionary_list_from_csv(CSV_DICTIONARY)
        self.assertEqual(len(result),2)
        self.assertEqual(result[1]["name"],"george")
        
        self.assertIn("noise",result[0])
        
    def test_guess_user_home_from_path(self):
        
        def r(path):
            return os.path.realpath(path)+"/"
        
        path=MOCK_FILES+"/heimdall/homes/smco500/maestro_suites/preop_zdps/"
        expected=r(MOCK_FILES+"/heimdall/homes/smco502/")
        result=guess_user_home_from_path(path)
        self.assertEqual(result,expected)
        
        "use realpath to explore parent folders for home tests"
        path=MOCK_FILES+"/heimdall/suites_with_codes/w5/"
        expected=r(MOCK_FILES+"/heimdall/homes/smco502/")
        result=guess_user_home_from_path(path)
        self.assertEqual(result,expected)
        
        path=os.environ["HOME"]+"/this-folder-does-not-exist-probably/123/"
        expected=r(os.environ["HOME"]+"/")
        result=guess_user_home_from_path(path)
        self.assertEqual(result,expected)
        
    def test_nodelogger_signals(self):
        
        task_text="""${destination}/${ENVAR_output_banco_name}.postalt.${outputfile}
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
        results=get_nodelogger_signals_from_task_text(task_text)
        signals=[r["signal"] for r in results]
        expected=["infox","abort"]
        self.assertEqual(signals,expected)
        
    def test_context_guess(self):
        paths={CONTEXT_GUESS_HOMES+"smco500/.suites/zdps":SCANNER_CONTEXT.OPERATIONAL,
               CONTEXT_GUESS_HOMES+"smco502/.suites/zdps":SCANNER_CONTEXT.OPERATIONAL,
               CONTEXT_GUESS_HOMES+"smco502/maestro_suites/zdps":SCANNER_CONTEXT.OPERATIONAL,
               CONTEXT_GUESS_HOMES+"smco502/.suites/preop_zdps":SCANNER_CONTEXT.PREOPERATIONAL,
               CONTEXT_GUESS_HOMES+"smco501/.suites/zdps":SCANNER_CONTEXT.PARALLEL,
               CONTEXT_GUESS_HOMES+"smco500/maestro_suites/zdps":SCANNER_CONTEXT.OPERATIONAL,
               G0_MINI_ME_PATH:SCANNER_CONTEXT.TEST}
        
        for path,expected in paths.items():
            msg="\npath = '%s'"%path
            self.assertTrue(os.path.exists(path),msg=msg)
            result=guess_scanner_context_from_path(path)
            self.assertEqual(result,expected,msg=msg)
        
        
        
        
        
        
        
        