import os.path
import re

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import file_cache
from heimdall.message_manager import hmm
from utilities.maestro import is_empty_module
from utilities.heimdall import find_critical_errors
from utilities import xml_cache

class ExperimentScanner():
    def __init__(self,path,critical_error_is_exception=True):
        
        if not path.endswith("/"):
            path+="/"
        
        self.path=path
        self.maestro_experiment=None        
        self.codes=set()
        self.messages=[]
        
        critical_errors=find_critical_errors(path)        
        for code,kwargs in critical_errors.items():
            description=hmm.get(code,**kwargs)
            self.add_message(code,description)
        if critical_errors:
            if critical_error_is_exception:
                raise ValueError("Experiment path:\n'%s'\nhas critical errors:\n%s"%(path,str(critical_errors)))
            return
        
        self.maestro_experiment=MaestroExperiment(path)
        
        self.index_experiment_files()
        self.scan_required_folders()
        self.scan_xmls()
        self.scan_scattered_modules()
        self.scan_node_names()
        self.scan_broken_symlinks()
        
    def add_message(self,code,description,url=""):        
        label=hmm.get_label(code)        
        if not url:
            url=hmm.get_url(code)
            
        message={"code":code,"label":label,"description":description,"url":url}
        self.codes.add(code)
        self.messages.append(message)
        
    def scan_scattered_modules(self):
        
        """
        This dictionary is necessary because 'modules/module1/flow.xml'
        may define '<MODULE name=module2>' at its root.      
        This dictionary has all aliases.
        """
        source_to_target={}
        
        not_empty_modules=[]
        module_element_to_flow_path={}
                
        for flow_path in self.flow_files:
            module_name=os.path.basename(os.path.dirname(flow_path))
            realname=os.path.basename(os.path.realpath(os.path.dirname(flow_path)))
            if realname!=module_name:
                source_to_target[module_name]=realname
            
            root=xml_cache.get(flow_path)
            not_empty_modules+=xml_cache.get_elements_of_tag(root,"MODULE")
            for m in not_empty_modules:
                module_element_to_flow_path[m]=flow_path
        
        """
        key is module realname
        value is list of flow.xml paths defining this module, if the
        list length is greater than 1 our module is scatterd
        """
        module_declares={}
        
        for m in not_empty_modules:
            module_name=m.attrib.get("name")
            if not module_name:
                continue
            
            realname=source_to_target.get(module_name,module_name)
            if realname not in module_declares:
                module_declares[realname]=[]
                
            flow_path=module_element_to_flow_path[m]
            module_declares[realname].append(flow_path)
        
        for module_name,flow_paths in module_declares.items():
            if len(flow_paths)>1:
                code="e5"
                flow_xmls="\n".join(flow_paths)
                description=hmm.get(code,
                                    module_name=module_name,
                                    flow_xmls=flow_xmls)
                self.add_message(code,description)                
        
    def scan_required_folders(self):        
        required_folders=("listings","sequencing","stats","logs")
        missing=[]
        for folder in required_folders:
            if not file_cache.isdir(self.path+folder):
                missing.append(folder)
        if missing:
            folders_msg=", ".join(missing)
            code="e1"
            description=hmm.get(code,folders=folders_msg)
            self.add_message(code,description)
        
    def scan_broken_symlinks(self):
        code="e4"
        for path in self.files:
            if not file_cache.islink(path):
                continue
            if file_cache.is_broken_symlink(path):
                target=file_cache.readlink(path)
                description=hmm.get(code,source=path,target=target)
                self.add_message(code,description)
        
    def scan_node_names(self):
        code="e3"
        r=re.compile(r"[a-zA-Z_]+[a-zA-Z0-9_]+")
        for task_path in self.task_files:
            task_name=task_path.split("/")[-1]
            if not r.match(task_name):           
                description=hmm.get(code,task_name=task_name,task_path=task_path)
                self.add_message(code,description)
        
    def scan_xmls(self):
        code="e2"
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
                    
        "also add parent folders of all folders, as long as they are in the experiment"
        for folder in list(folders):
            parent=folder
            while parent.startswith(self.path):
                if parent!=folder:
                    folders.add(parent)
                parent=os.path.dirname(parent)
                    
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
















