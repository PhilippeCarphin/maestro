
import unittest

from heimdall.message_manager import hmm

class TestHeimdallMessageManager(unittest.TestCase):
            
    def test_exceptions(self):
        
        def get_bad_code():
            hmm.get("does not exist")
        self.assertRaises(ValueError,get_bad_code)
        
        def get_bad_format():
            hmm.get("e001",not_a_keyword="abc")
        self.assertRaises(ValueError,get_bad_format)
                
        def get_extra_format():
            hmm.get("e001",folders="123",not_a_keyword="abc")
        self.assertRaises(ValueError,get_extra_format)
        
        folders=["abc","123"]
        result=hmm.get("e001",folders=folders)
        description=hmm._code_to_csv["e001"]["description"]
        expected=description.format(folders=str(folders))
        self.assertEqual(expected,result)