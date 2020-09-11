
import unittest

from heimdall.message_manager import hmm, MESSAGE_TOKEN_REGEX


class TestHeimdallMessageManager(unittest.TestCase):

    def test_exceptions(self):

        def get_bad_code():
            hmm.get("does not exist")
        self.assertRaises(ValueError, get_bad_code)

        def get_bad_format():
            hmm.get("e001", not_a_keyword="abc")
        self.assertRaises(ValueError, get_bad_format)

        def get_extra_format():
            hmm.get("e001", folders="123", not_a_keyword="abc")
        self.assertRaises(ValueError, get_extra_format)

        folders = ["abc", "123"]
        result = hmm.get("e001", folders=folders)
        description = hmm._code_to_csv["e001"]["description_en"]
        expected = description.format(folders=str(folders))
        self.assertEqual(expected, result)
    
    def test_english_french_csv(self):
        "English and French in CSV match each other."
        
        "every label/description has both en/fr"
        missing_en=[]
        missing_fr=[]
        for code,data in hmm._code_to_csv.items():
            for prefix in ("label_","description_"):
                en=data.get(prefix+"en")
                fr=data.get(prefix+"fr")
                if not en:
                    missing_en.append(prefix)
                if not fr:
                    missing_fr.append(prefix)
        self.assertFalse(missing_en)
        self.assertFalse(missing_fr)
        
        "descriptions for en/fr have identical {} tokens"
        for code,data in hmm._code_to_csv.items():
            en=data.get("description_en")
            fr=data.get("description_fr")
            en_tokens=set(MESSAGE_TOKEN_REGEX.findall(en))
            fr_tokens=set(MESSAGE_TOKEN_REGEX.findall(fr))
            msg="\nen = '%s'\nfr = '%s'"%(en,fr)
            self.assertEqual(en_tokens,fr_tokens,msg=msg)
        
        
        
        
        
        
