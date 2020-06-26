import re

from utilities import get_dictionary_list_from_csv
from constants.path import HEIMDALL_MESSAGE_CSV

class HeimdallMessageManager():
    def __init__(self):        
        csv_list=get_dictionary_list_from_csv(HEIMDALL_MESSAGE_CSV)   
        self._code_to_csv={item["code"]:item for item in csv_list}
        self.codes=sorted([item["code"] for item in csv_list])
        
        self._token_regex=re.compile(r"{[a-zA-Z_]+}")
        
    def get_label(self,code):
        data=self._code_to_csv[code]
        return data["label"]
    
    def get_url(self,code):
        data=self._code_to_csv[code]
        return data.get("url","")
    
    def get(self,code,**kwargs):
        """
        Return the message for this code, formatted with these keyword arguments.
        Raises an exception if:
            * The message has unused format tokens like '{cat}'
            * The code does not exist.
        Since all codes have tests in theory, this function rules out the possibility
        of badly formatted messages or code typos.
        """
        
        data=self._code_to_csv.get(code)
        if not data:
            raise ValueError("code '%s' does not exist in Heimdall messages."%code)
        
        description=data.get("description","")
        
        description=description.replace("\\n","\n")
        
        for key in kwargs:
            if "{"+key+"}" not in description:
                raise ValueError("code '%s' was given an extra string format key not found in message CSV: '%s'"%(code,key))
                
        message=description.format(**kwargs)
        
        matches=self._token_regex.findall(message)
        if matches:
            raise ValueError("Unused keyword arguments in Heimdall message for code '%s': "%(code,str(matches)))
        
        return message

heimdall_message_manager=HeimdallMessageManager()
hmm=heimdall_message_manager