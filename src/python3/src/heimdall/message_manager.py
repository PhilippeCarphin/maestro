import re

from utilities import get_dictionary_list_from_csv
from constants.path import HEIMDALL_MESSAGE_CSV
from constants.heimdall import DEFAULT_LANGUAGE, LANGUAGES

"""
Find curly tokens in the heimdall message CSV.
Example:
    No {exp_path} found in ${{EXP_HOME}}
Matches:
    {exp_path}
but not:
    ${{EXP_HOME}}
"""
MESSAGE_TOKEN_REGEX=re.compile(r"(?<!{){[a-zA-Z_]+}(?!})")

class HeimdallMessageManager():
    def __init__(self):

        self.parse_message_codes_csv()

    def parse_message_codes_csv(self):

        path = HEIMDALL_MESSAGE_CSV
        csv_list = get_dictionary_list_from_csv(path)
        self._code_to_csv = {item["code"]: item for item in csv_list}
        self.codes = sorted([item["code"] for item in csv_list])

        "check for duplicate codes"
        duplicates = [c for c in self.codes if self.codes.count(c) > 1]
        if duplicates:
            raise ValueError("Message code CSV '%s' has duplicate code entries: %s" % (path, ", ".join(duplicates)))

        "check for invalid code format"
        regex_string = "[cewib][0-9]+"
        r = re.compile(regex_string)
        bad_codes = [c for c in self.codes if not r.match(c)]
        if bad_codes:
            raise ValueError("Message code CSV '%s' has bad code entries: %s\nCodes must match regex:\n   %s" % (path, ", ".join(bad_codes), regex_string))
            
    def get_csv_value_or_default(self, code, key_prefix, language):
        """
        For example:
            ("c001", "label", "fr")
        will attempt to return the value for "c001" from the message CSV with the column "label_fr".
        
        If language doesn't exist or the cell value is empty, use "en".
        """
        
        data = self._code_to_csv[code]
        
        if language not in LANGUAGES:
            language=DEFAULT_LANGUAGE
            
        key=key_prefix+"_"+language
        value=data.get(key,"")
        if value:
            return value
        
        key=key_prefix+"_"+DEFAULT_LANGUAGE
        return data.get(key,"")
        
    def get_label(self, code, language="en"):
        return self.get_csv_value_or_default(code,"label",language)

    def get_url(self, code, language="en"):
        return self.get_csv_value_or_default(code,"url",language)

    def get(self, code, **kwargs):
        """
        Return the message for this code, formatted with these keyword arguments.
        Raises an exception if:
            * The message has unused format tokens like '{cat}'
            * The code does not exist.
        Since all codes have tests in theory, this function rules out the possibility
        of badly formatted messages or code typos.
        """
        
        language=kwargs.get("language")
        if language not in LANGUAGES:
            language=DEFAULT_LANGUAGE
            
        data = self._code_to_csv.get(code)
        if not data:
            raise ValueError("code '%s' does not exist in Heimdall messages." % code)

        description = self.get_csv_value_or_default(code,"description",language)
        description = description.replace("\\n", "\n")
        tokens = MESSAGE_TOKEN_REGEX.findall(description)
        
        for key in kwargs:
            
            if key == "language":
                continue
            
            if "{"+key+"}" not in description:
                raise ValueError("code '%s' was given an extra string format key not found in message CSV: '%s'" % (code, key))

        message = description.format(**kwargs)

        unused_tokens = [t for t in tokens if t in message]
        if unused_tokens:
            raise ValueError("Unused keyword arguments in Heimdall message for code '%s': %s" % (code, str(unused_tokens)))

        return message


heimdall_message_manager = HeimdallMessageManager()
hmm = heimdall_message_manager
