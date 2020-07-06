import os.path
import re
from collections import OrderedDict
import Levenshtein

from constants import NODELOGGER_SIGNALS, SCANNER_CONTEXT, NODE_TYPE, HEIMDALL_CONTENT_CHECKS_CSV

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import file_cache
from heimdall.message_manager import hmm
from utilities.maestro import is_empty_module, get_weird_assignments_from_config_text
from utilities.heimdall.critical_errors import find_critical_errors
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_path
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities import print_red, print_orange, print_yellow, print_green, print_blue
from utilities import xml_cache, get_dictionary_list_from_csv, guess_user_home_from_path
from utilities.qstat import get_qstat_queues

class ExperimentScanner():
    def __init__(self,
                 path,
                 context=None,
                 critical_error_is_exception=True,
                 debug_qstat_queue_override=""):
        
        if not path.endswith("/"):
            path+="/"
        
        self.path=path
        self.maestro_experiment=None        
        self.codes=set()
        self.messages=[]
        
        """
        Instead of running the qstat shell command, use this output instead.
        Useful for debugging/tests.
        """
        self.debug_qstat_queue_override=debug_qstat_queue_override
                
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
        
        if not context:
            context=guess_scanner_context_from_path(self.path)
        self.context=context
        
        self.scan_required_folders()
        self.scan_required_files()
        self.scan_all_file_content()
        self.scan_exp_options()
        self.scan_xmls()
        self.scan_resource_files()
        self.scan_resource_queue_definitions()
        self.scan_config_files()
        self.scan_home_soft_links()
        self.scan_scattered_modules()
        self.scan_all_task_content()
        self.scan_node_names()
        self.scan_broken_symlinks()
        
    def is_context_operational(self):
        return self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                    SCANNER_CONTEXT.PREOPERATIONAL)
        
    def add_message(self,code,description,url=""):        
        label=hmm.get_label(code)        
        if not url:
            url=hmm.get_url(code)
            
        message={"code":code,"label":label,"description":description,"url":url}
        self.codes.add(code)
        self.messages.append(message)
        
    def parse_file_content_checks_csv(self):
        """
        Sanity check the file content CSV and make the dictionaries more convenient to use.
        They are transformed into:
            {
               "code":"w7",
               "filetypes":["tsk","cfg"],
               "substring":"",
               "regex_string":"",
               "regex":<re.compile-result>,
               "description_suffix":""
            }
        """
        path=HEIMDALL_CONTENT_CHECKS_CSV
        
        "filetype must be one of these"
        valid_filetypes=["tsk","cfg","xml","resource_xml"]
        
        "list of check data, each row of CSV is a check data"
        self.file_content_checks=get_dictionary_list_from_csv(path)
        
        "key is filetype, value is list of check_data that apply to it"
        self.filetype_to_check_datas={filetype:[] for filetype in valid_filetypes}
        
        for check_data in self.file_content_checks:
            if check_data["regex_string"]:
                try:
                    check_data["regex"]=re.compile(check_data["regex_string"])
                except re.error:
                    raise ValueError("Bad regex string '%s' in file content CSV: '%s'"%(check_data["regex string"],path))
            
            if not check_data["regex_string"] and not check_data["substring"]:
                raise ValueError("All columns in file content CSV require either substring or regex string: '%s'"%path)
            
            filetypes=[i.strip() for i in check_data["filetypes"].split(",")]
            if "all" in filetypes:
                filetypes=valid_filetypes
            invalid=[i for i in filetypes if i not in valid_filetypes]
            if not filetypes or invalid:
                raise ValueError("Bad filetype arguments '%s' in file content CSV: '%s'"%(str(invalid),path))
            check_data["filetypes"]=filetypes
            
            for filetype in filetypes:
                self.filetype_to_check_datas[filetype].append(check_data)
    
    def scan_resource_queue_definitions(self):
        """
        If qstat queue "123" does not exist, finds cases like:
            FRONTEND_DEFAULT_Q=123
        """
        
        queues=get_qstat_queues(cmd_output_override=self.debug_qstat_queue_override)
        names=["FRONTEND_DEFAULT_Q",
               "FRONTEND_XFER_Q",
               "FRONTEND_DAEMON_Q",
               "BACKEND_DEFAULT_Q",
               "BACKEND_XFER_Q"]
        for name in names:
            value=self.maestro_experiment.get_resource_value_from_key(name)
            if value and value not in queues:
                code="w10"
                description=hmm.get(code,
                                    value=value,
                                    name=name,
                                    queues=str(queues))
                self.add_message(code,description)
        
    def scan_config_files(self):
        "scan the content of config files (see scan_file_content for CSV content scan)"
        
        code="e10" if self.is_context_operational() else "w6"
        for path in self.config_files:
            content=file_cache.open(path)
            data=get_weird_assignments_from_config_text(content)
            for section,d in data.items():
                for key,value in d.items():
                    if value.startswith("/"):
                        description=hmm.get(code,
                                            config_path=path,
                                            bad_path=value)
                        self.add_message(code,description)
                
    def scan_resource_files(self):
        "scan the content of resource files (see scan_file_content for CSV content scan)"
        
        """
        this regex matches strings like:
            machine="${FRONTEND}"
        where group 1 is the value between double quotes.
        """
        attribute_regex=re.compile(r"""[a-zA-Z_]+[ ]*=[ ]*["']([^'"]+)["']""")
        me=self.maestro_experiment
        
        "undefined variables"
        d=me.undefined_resource_variables
        if d:            
            for path,variables in d.items():
                code="e12"
                description=hmm.get(code,
                                    resource_path=path,
                                    variable_names=str(variables))
                self.add_message(code,description)
        
        "resources.def variable name typo"
        standard_resource_defines=["FRONTEND",
                                 "BACKEND",
                                 "FRONTEND_DEFAULT_Q",
                                 "FRONTEND_XFER_Q",
                                 "FRONTEND_DAEMON_Q",
                                 "BACKEND_DEFAULT_Q",
                                 "BACKEND_XFER_Q"]
        
        for name in standard_resource_defines:
            for path,declares in me.path_to_resource_declares.items():
                if name in declares:
                    continue
                for maybe_typo in declares:
                    d=Levenshtein.distance(name,maybe_typo)
                    if d==1:
                        code="w9"
                        description=hmm.get(code,
                                            maybe_typo=maybe_typo,
                                            expected=name)
                        self.add_message(code,description)
    
    
        for path in self.resource_files:            
            "unbalanced parentheses"
            code="e9"
            content=file_cache.open(path)
            for match in attribute_regex.finditer(content):
                attribute_value=match.group(1)
                if attribute_value.count("{") != attribute_value.count("}"):                    
                    description=hmm.get(code,
                                        attribute_value=attribute_value,
                                        file_path=path)
                    self.add_message(code,description)
            
            "dependency codes"
            etree=file_cache.etree_parse(path)
            elements=etree.xpath("//DEPENDS_ON")
            for d_element in elements:
                
                "hard coded dependency experiment path"
                exp=d_element.get("exp")
                if exp and exp.startswith("/"):
                    
                    if file_cache.isdir(exp):
                        code="b1"
                    else:
                        code="e11"
                    
                    description=hmm.get(code,
                                        exp_value=exp,
                                        resource_path=path)
                    self.add_message(code,description)                
                
    def scan_home_soft_links(self):
        """
        Find core maestro files with a realpath outside the user home containing this project.
        """
        
        home_root=guess_user_home_from_path(self.path)
        bad_links=[]
        
        for path in self.files:
            realpath=file_cache.realpath(path)
            if not realpath.startswith(home_root):
                bad_links.append(path)
                
        if bad_links:
            is_op=self.is_context_operational()
            code="w5" if is_op else "i1"
            description=hmm.get(code,
                                real_home=home_root,
                                bad_links=bad_links)
            self.add_message(code,description)
                
    def scan_all_file_content(self):
        """
        See scan_file_content
        """        
        self.parse_file_content_checks_csv()
        
        for path in self.files:
            self.scan_file_content(path)
            
    def scan_file_content(self,path):
        """
        Use the file content CSV to scan for substrings and regexes in file content.
        
        This function only does generic content scans using the CSV, nothing specific
        to one code.
        """        
        rpath=self.maestro_experiment.path+"resources/"
        filetype=None
        for extension in ("tsk","cfg","xml"):
            if path.endswith("."+extension):
                filetype=extension
                break
        if path.startswith(rpath) and path.endswith(".xml"):
            filetype="resource_xml"
        
        if not filetype:
            "files of unknown type are not content scanned"
            return
        
        content=file_cache.open_without_comments(path)    
        for check_data in self.filetype_to_check_datas[filetype]:
            
            found_substring=bool(check_data["substring"]) and check_data["substring"] in content
            found_regex=check_data.get("regex") and bool(check_data.get("regex").search(content))
                        
            "describe what was found"
            search="search"
            if found_regex:
                search="regex '%s'"%check_data["regex_string"]
            if found_substring:
                search="substring '%s'"%check_data["substring"]
                
            if found_substring or found_regex:
                description=hmm.get(check_data["code"],
                                    search=search,
                                    file_path=path)
                self.add_message(check_data["code"],description)
        
    def scan_required_files(self):
        
        is_op=self.is_context_operational()
        
        for node_path,node_data in self.maestro_experiment.node_datas.items():
            node_type=node_data["type"]
            resource_path=node_data["resource_path"]
            task_path=node_data["task_path"]
            
            if file_cache.exists(resource_path):
                continue
            
            if node_type==NODE_TYPE.TASK:
                kwargs={"task_path":task_path,
                        "resource_path":resource_path}
                
                if is_op:
                    code="e7"
                    kwargs["context"]=self.context
                else:
                    code="w1"
                
                description=hmm.get(code,**kwargs)
                self.add_message(code,description)
                
            elif node_type==NODE_TYPE.LOOP:
                code="w2"
                description=hmm.get(code,
                                    node_path=node_path,
                                    resource_path=resource_path)
                self.add_message(code,description)
        
    def scan_all_task_content(self):        
        for task_path in self.task_files:
            self.scan_task(task_path)
            
    def scan_task(self,task_path):
        
        "find invalid nodelogger signals"
        results=get_nodelogger_signals_from_task_path(task_path)
        for result in results:
            if result["signal"] not in NODELOGGER_SIGNALS:
                code="e6"
                description=hmm.get(code,
                                    bad_signal=result["signal"],
                                    line_number=result["line_number"],
                                    task_path=task_path)
                self.add_message(code,description)
        
    def scan_scattered_modules(self):
        
        """
        This dictionary is necessary because 'modules/module1/flow.xml'
        may define '<MODULE name=module2>' at its root.      
        This dictionary has all aliases.
        """
        source_to_target={}
        
        module_element_to_flow_path={}
                
        for flow_path in self.flow_files:
            module_name=os.path.basename(os.path.dirname(flow_path))
            realname=os.path.basename(os.path.realpath(os.path.dirname(flow_path)))
            if realname!=module_name:
                source_to_target[module_name]=realname
            
            root=xml_cache.get(flow_path)
            modules=xml_cache.get_elements_of_tag(root,"MODULE")
            for m in modules:
                module_element_to_flow_path[m]=flow_path
        
        not_empty_modules=[m for m in module_element_to_flow_path if not is_empty_module(m)]
        
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
        broken=[path for path in self.files if file_cache.is_broken_symlink(path)]
        if broken:
            broken_links="\n".join(broken)
            description=hmm.get(code,broken_links=broken_links)
            self.add_message(code,description)
        
    def scan_node_names(self):
        code="e3"
        r=re.compile(r"[a-zA-Z_]+[a-zA-Z0-9_]+")
        for task_path in self.task_files:
            task_name=task_path.split("/")[-1]
            if not r.match(task_name):           
                description=hmm.get(code,task_name=task_name,task_path=task_path)
                self.add_message(code,description)
    
    def scan_exp_options(self):
        xml_path=self.maestro_experiment.path+"ExpOptions.xml"
        support_status=self.maestro_experiment.get_support_status()
        url_regex=re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")                                     
                             
        "multiple support info elements"
        root=file_cache.etree_parse(xml_path)
        if root is not None:
            support_infos=root.xpath("//SupportInfo")
            if len(support_infos)>1:
                code="w8"
                description=hmm.get(code,
                                    xml_path=xml_path)
                self.add_message(code,description)
                             
        if support_status:
            
            "max length"
            max_chars=50
            if len(support_status)>max_chars:
                code="b2"
                description=hmm.get(code,
                                    xml_path=xml_path,
                                    char_count=len(support_status),
                                    max_chars=max_chars)
                self.add_message(code,description)
            
            "has url"
            if not url_regex.search(support_status):
                code="b3"
                description=hmm.get(code,
                                    xml_path=xml_path)
                self.add_message(code,description)
            
            "reasonable start string like 'full support' "
            found_substring=False
            stripped_status=re.sub("[ -_]+","",support_status.lower())
            substrings=["Full","Daytime","Business","Office","None"]
            for substring in substrings:
                if stripped_status.startswith(substring.lower()):
                    found_substring=True
                    break
            if not found_substring:
                code="b4"
                description=hmm.get(code,
                                    xml_path=xml_path,
                                    substrings=str(substrings))
                self.add_message(code,description)
                
        "no support status in op"
        is_op=self.is_context_operational()
        if not support_status and is_op:
            code="w7"
            description=hmm.get(code,
                                xml_path=xml_path)
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
        rpath=self.path+"resources/"
        mpath=self.path+"modules/"
        
        "flow.xml files in modules folder"
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
                    
                    "also add resource XMLs that were not discovered by using the flow"
                    if path.startswith(rpath) and path.endswith(".xml"):
                        resource_files.add(path)
                
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
    
    def get_report_text(self):
        lines=[]
        for m in self.messages:
            line="%s: %s\n%s"%(m["code"],m["label"],m["description"])
            lines.append(line)
        return "\n\n".join(lines)
    
    def print_report(self,use_colors=True):
        char_color_functions=OrderedDict([("c",print_red),
                                          ("e",print_orange),
                                          ("w",print_yellow),
                                          ("i",print_green),
                                          ("b",print_blue)])
        
        for c,f in char_color_functions.items():
            for message in self.messages:
                code=message["code"]
                if not code.startswith(c):
                    continue
                f(code+": "+message["label"])
                print(message["description"])
        
        print("\nHeimdall found %s items to report for maestro suite:\n    %s"%(len(self.messages),self.path))
















