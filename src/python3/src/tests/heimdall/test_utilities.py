
from tests.path import CSV_DICTIONARY

import unittest

from utilities import get_dictionary_list_from_csv
from utilities.heimdall import get_nodelogger_signals_from_task_text

class TestUtilities(unittest.TestCase):
            
    def test_csv_dictionary(self):
        result=get_dictionary_list_from_csv(CSV_DICTIONARY)
        self.assertEqual(len(result),2)
        self.assertEqual(result[1]["name"],"george")
        
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
        