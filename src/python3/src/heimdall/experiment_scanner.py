import os.path
import re

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import file_cache
from heimdall.message_manager import hmm
from utilities.heimdall import find_blocking_errors

class ExperimentScanner():
    def __init__(self,path,blocking_errors_is_exception=True):
        
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
            if blocking_errors_is_exception:
                raise ValueError("Experiment path:\n'%s'\nhas blocking errors:\n%s"%(path,str(blocking_errors)))
            return
        
        self.maestro_experiment=MaestroExperiment(path)
        
        self.index_experiment_files()
        self.scan_xmls()
        self.scan_node_names()
        self.scan_broken_symlinks()
        
    def add_message(self,code,description,url=""):        
        label=hmm.get_label(code)        
        if not url:
            url=hmm.get_url(code)
            
        message={"code":code,"label":label,"description":description,"url":url}
        self.codes.add(code)
        self.messages.append(message)
        
    def scan_broken_symlinks(self):
        code="e7"
        for path in self.files:
            if not file_cache.islink(path):
                continue
            if file_cache.is_broken_symlink(path):
                target=file_cache.readlink(path)
                description=hmm.get(code,source=path,target=target)
                self.add_message(code,description)
        
    def scan_node_names(self):
        code="e6"
        r=re.compile(r"[a-zA-Z_]+[a-zA-Z0-9_]+")
        for task_path in self.task_files:
            task_name=task_path.split("/")[-1]
            if not r.match(task_name):           
                description=hmm.get(code,task_name=task_name,task_path=task_path)
                self.add_message(code,description)
        
    def scan_xmls(self):
        code="e5"
        for path in self.xml_files:
            if file_cache.etree_parse(path) is None:
                description=hmm.get(code,xml=path)
                self.add_message(code,description)
        
    def index_experiment_files(self):
        """
        Quickly find the path of all files that are in (or should be in)
        the maestro experiment repo: tsk, cfg, xml, and more.
        
        We cannot simply do a recursive search, because soft links sometimes
        lead to massive folders outside the experiment.
        """
        
        paths=set()
        folders=set()        
        resource_files=set()
        flow_files=set()
        
        "flow.xml files in modules folder"
        mpath=self.path+"modules"
        for folder in file_cache.listdir(mpath):
            flow=mpath+"flow.xml"
            if file_cache.isfile(flow):
                paths.add(flow)
                flow_files.add(flow)
        
        "find maestro files discovered through flow.xml"
        for node_path in self.maestro_experiment.get_node_datas():
            for prefix in ("task","resource","config","flow"):
                path=node_path[prefix+"_path"]
                if not path:
                    continue
                folder=os.path.dirname(path)
                folders.add(folder)
                
                if not file_cache.isfile(path):
                    continue
                paths.add(path)
                if prefix=="resource":
                    resource_files.add(path)
                elif prefix=="flow":
                    flow_files.add(path)
                    
        "find maestro files (including broken symlinks) not in flow.xml, but in the same folders"
        for folder in folders:
            if not file_cache.isdir(folder):
                continue
            for filename in file_cache.listdir(folder):
                path=folder+"/"+filename
                if file_cache.isfile(path) or file_cache.is_broken_symlink(path):
                    paths.add(path)
                    
        "index tsk cfg xml"
        task_files=[]
        config_files=[]
        xml_files=[]
        for path in paths:
            if path.endswith(".tsk"):
                task_files.append(path)
            elif path.endswith(".cfg"):
                config_files.append(path)
            elif path.endswith(".xml"):
                xml_files.append(path)
        
        "all full paths to all files to scan"
        self.files=sorted(list(paths))
        
        "all folders containing files to scan"
        self.folders=sorted(list(folders))
        
        "all cfg files"
        self.config_files=sorted(config_files)
        
        "all flow.xml files"
        self.flow_files=sorted(list(flow_files))
        
        "all resource xml files"
        self.resource_files=sorted(list(resource_files))
        
        "all tsk files"
        self.task_files=sorted(task_files)
        
        "all xml files"
        self.xml_files=sorted(xml_files)
















