
from heimdall.basic_validation import find_blocking_error
from maestro.experiment import MaestroExperiment
from heimdall import hmm

class ExperimentScanner():
    def __init__(self,path):
        
        self.path=path
        
        self.codes=set()
        self.messages=[]
        
        code,description=find_blocking_error(path)
        if description:
            self.add_message(code,description)
        
        self.maestro_experiment=MaestroExperiment(path)
    
    def add_message(self,code,description,url=""):
        
        label=hmm.get_label(code)        
        if not url:
            url=hmm.get_url(code)
            
        message={"code":code,"label":label,"description":description,"url":url}
        self.codes.add(code)
        self.messages.append(message)
            