
from maestro_experiment import MaestroExperiment
from heimdall.message_manager import hmm
from utilities.heimdall import find_blocking_errors

class ExperimentScanner():
    def __init__(self,path):
        
        if not path.endswith("/"):
            path+="/"
        
        self.path=path
        self.maestro_experiment=None        
        self.codes=set()
        self.messages=[]
        
        blocking_errors=find_blocking_errors(path)        
        for code,kwargs in blocking_errors.items():
            description=hmm.get(code,**kwargs)
            self.add_message(code,description)
        if blocking_errors:
            return
        
        self.maestro_experiment=MaestroExperiment(path)
    
    def add_message(self,code,description,url=""):
        
        label=hmm.get_label(code)        
        if not url:
            url=hmm.get_url(code)
            
        message={"code":code,"label":label,"description":description,"url":url}
        self.codes.add(code)
        self.messages.append(message)
            