import os.path
import re
from collections import OrderedDict
import Levenshtein

from constants import NODELOGGER_SIGNALS, SCANNER_CONTEXT, NODE_TYPE, HEIMDALL_CONTENT_CHECKS_CSV, EXPECTED_CONFIG_STATES, HUB_PAIRS

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import file_cache
from heimdall.message_manager import hmm
from home_logger import logger
from utilities.maestro import is_empty_module, get_weird_assignments_from_config_text, get_commented_pseudo_xml_lines
from utilities.heimdall.critical_errors import find_critical_errors
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_path, get_levenshtein_pairs, get_resource_limits_from_batch_element
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities.heimdall.path import get_ancestor_folders, is_editor_swapfile
from utilities import print_red, print_orange, print_yellow, print_green, print_blue
from utilities import xml_cache, get_dictionary_list_from_csv, guess_user_home_from_path, get_links_source_and_target
from utilities.qstat import get_qstat_data_from_text, get_qstat_data, get_resource_limits_from_qstat_data
from utilities.shell import safe_check_output_with_status

"""
Matches codes like 'e001' and 'c010'
"""
CODE_REGEX=re.compile("[cewib][0-9]{3}")

class ExperimentScanner():
    def __init__(self,
                 path,
                 context=None,
                 operational_home=None,
                 parallel_home=None,
                 critical_error_is_exception=True,
                 debug_qstat_output_override=""):
        
        if not path.endswith("/"):
            path+="/"
        
        self.path=path
        self.maestro_experiment=None
        self.codes=set()
        self.messages=[]
        
        """
        Some scans like suite in the overview XML requires knowing the op/par home.
        Some scans may not care, so only throw a "does not exist" error
        if string has a value.
        """
        if operational_home and not os.path.exists(operational_home):
            raise ValueError("Home path for operational user does not exist: '%s'"%operational_home)
        if parallel_home and not os.path.exists(parallel_home):
            raise ValueError("Home path for parallel user does not exist: '%s'"%parallel_home)
        self.operational_home=operational_home
        self.parallel_home=parallel_home
        
        """
        Instead of running the qstat shell command, use this output instead.
        Useful for debugging/tests.
        """
        if debug_qstat_output_override:
            self.qstat_data=get_qstat_data_from_text(debug_qstat_output_override)
        else:
            self.qstat_data=get_qstat_data(timeout=3)
                
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
        self.scan_extra_files()
        self.scan_all_file_content()
        self.scan_exp_options()
        self.scan_xmls()
        self.scan_hub()
        self.scan_git_repo()
        self.scan_deprecated_files_folders()
        self.scan_resource_files()
        self.scan_resource_queues()
        self.scan_overview_xmls()
        self.scan_config_files()
        self.scan_home_soft_links()
        self.scan_modules()
        self.scan_all_task_content()
        self.scan_node_names()
        self.scan_broken_symlinks()
        
        self.sort_messages()
        
    def sort_messages(self):
        
        def sort_key(a):
            levels="cewib"
            return str(levels.index(a["code"][0]))+a["code"][1:]
        
        self.messages=sorted(self.messages,key=sort_key)
        
    def is_context_operational(self):
        return self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                    SCANNER_CONTEXT.PREOPERATIONAL)
        
    def add_message(self,code,description,url=""):
        
        if not CODE_REGEX.match(code):
            raise ValueError("ExperimentScanner code '%s' does not match regex code regex:\n    %s"%(code,CODE_REGEX.pattern))
        
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
               "strip_comments":True|False,
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
                    r=check_data["regex_string"]
                    check_data["regex"]=re.compile(r)
                except re.error:
                    raise ValueError("Bad regex string '%s' in file content CSV: '%s'"%(check_data["regex string"],path))
            
            if not check_data["regex_string"] and not check_data["substring"]:
                raise ValueError("All columns in file content CSV require either substring or regex string: '%s'"%path)
            
            check_data["strip_comments"]=check_data["strip_comments"] == "yes"
            
            filetypes=[i.strip() for i in check_data["filetypes"].split(",")]
            if "all" in filetypes:
                filetypes=valid_filetypes
            invalid=[i for i in filetypes if i not in valid_filetypes]
            if not filetypes or invalid:
                raise ValueError("Bad filetype arguments '%s' in file content CSV: '%s'"%(str(invalid),path))
            check_data["filetypes"]=filetypes
            
            for filetype in filetypes:
                self.filetype_to_check_datas[filetype].append(check_data)
    
    def scan_git_repo(self):
        
        must_have_repo=self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                        SCANNER_CONTEXT.PREOPERATIONAL,
                                        SCANNER_CONTEXT.PARALLEL)
        must_be_clean=must_have_repo
        
        if file_cache.isdir(self.path+".git"):
            cmd="cd %s ; git status --porcelain"%self.path
            output,status=safe_check_output_with_status(cmd)
            has_repo=status==0
        else:
            output=""
            status=1
            has_repo=False
        
        if must_have_repo and not has_repo:
            code="e016"
            description=hmm.get(code,
                                context=self.context)
            self.add_message(code,description)
        
        if has_repo and output:
            if must_be_clean:
                code="w015"
                description=hmm.get(code,
                                    context=self.context)
            else:
                code="i004"
                description=hmm.get(code)
            self.add_message(code,description)
    
    def scan_extra_files(self):
        """
        Find extra files that probably don't belong in the project.
        """
        
        "text editor swap files"
        swaps=[path for path in self.files if is_editor_swapfile(path)]
        if swaps:
            code="i003"
            filenames="\n".join(swaps)
            if len(swaps)>1:
                filenames="\n"+filenames
            description=hmm.get(code,
                                swaps=filenames)
            self.add_message(code,description)            
        
        "Random files should not be adjacent to any maestro files like tsk, cfg, resource xml"        
        maestro_files=self.task_files+self.config_files+self.resource_files+self.flow_files
        maestro_files=sorted(list(set(maestro_files)))
        explored=set()
        
        for path in maestro_files:
            
            folder=os.path.dirname(path)
            if folder in explored:
                continue
            explored.add(folder)
            
            extra=[]
            for basename in file_cache.listdir(folder):
                path=folder+"/"+basename
                if file_cache.isfile(path) and path not in maestro_files:
                    extra.append(path)
            
            if extra:
                code="b006"
                filenames="\n".join(extra)
                if len(extra)>1:
                    filenames="\n"+filenames
                description=hmm.get(code,
                                    folder=folder,
                                    filenames=filenames)
                self.add_message(code,description)
                
        
    def scan_hub(self):
        "scan links and targets of hub folder"
        
        hub_items=[self.path+"hub/"+filename for filename in file_cache.listdir(self.path+"hub")]
        
        "items in hub that are not links to folders"
        if self.context in (SCANNER_CONTEXT.OPERATIONAL,
                            SCANNER_CONTEXT.PREOPERATIONAL,
                            SCANNER_CONTEXT.PARALLEL):
            bad=[]
            for path in hub_items:
                if not file_cache.islink(path) or not file_cache.isdir(path):
                    bad.append(path)
            if bad:
                code="e014"
                msg="\n".join(bad)
                if len(bad)>1:
                    msg="\n"+msg
                description=hmm.get(code,
                                    context=self.context,
                                    bad=msg)
                self.add_message(code,description)
        
        """
        dissimilar targets
        for example eccc-ppp3 and eccc-ppp4 should have nearly identical targets
        """
        max_levenshtein_distance=3
        hub=self.path+"hub/"
        source_and_target=get_links_source_and_target(hub)
        sources=[a["source"] for a in source_and_target]
        source_to_target={a["source"]:a["target"] for a in source_and_target}
        "find pairs like eccc-ppp3 and eccc-ppp4"
        lev_data=get_levenshtein_pairs(sources)
        pairs=lev_data["pairs"]
        "find pairs like banting and daley"
        for item1,item2 in HUB_PAIRS:
            path1=hub+item1
            path2=hub+item2
            if file_cache.exists(path1) and file_cache.exists(path2):
                pairs.append([path1,path2])
        
        for item1,item2 in pairs:
            target1=source_to_target[item1]
            target2=source_to_target[item2]
            target_d=Levenshtein.distance(target1,target2)
            if target_d > max_levenshtein_distance:
                folder1=os.path.basename(target1)
                folder2=os.path.basename(target2)
                code="w014"
                description=hmm.get(code,
                                    folder1=folder1,
                                    folder2=folder2,
                                    target1=target1,
                                    target2=target2)
                self.add_message(code,description)
            
                
    def scan_deprecated_files_folders(self):
        old=["hub/hare",
             "hub/brooks",
             "hub/eccc-ppp1",
             "hub/eccc-ppp2",
             "ExpDate",
             "ExpTimings",
             "flow.xml"]
        paths=[self.path+a for a in old]
        code="b005"
        deprecated=[path for path in paths if file_cache.exists(path)]
        if deprecated:
            msg="\n".join(deprecated)
            if len(deprecated)>1:
                msg="\n"+msg
            description=hmm.get(code,
                                deprecated=msg)
            self.add_message(code,description)
    
    def scan_overview_xmls(self):
        """
        Scan if this experiment is found in the correct or unexpected overview XMLs.
        """
        
        if not self.operational_home or not self.parallel_home:
            return
        
        context_to_path={SCANNER_CONTEXT.OPERATIONAL:self.operational_home+"/xflow.suites.xml",
                         SCANNER_CONTEXT.PREOPERATIONAL:self.operational_home+"/xflow_preop.suites.xml",
                         SCANNER_CONTEXT.PARALLEL:self.parallel_home+"/xflow.suites.xml"}
        
        if self.context not in context_to_path:
            return
        
        realpath=file_cache.realpath(self.path)
        
        for context,xml_path in context_to_path.items():
            
            root=file_cache.etree_parse(xml_path)
            
            if root is None:
                """
                while it is a serious problem that the overview XML did not parse,
                it is not a problem belonging to the suite.            
                """
                return
            
            experiments=[file_cache.realpath(e.text) for e in root.xpath("//Exp")]
            should_be_in_xml=self.context==context
            
            if should_be_in_xml and realpath not in experiments:
                code="w011"
                description=hmm.get(code,
                                    context=self.context,
                                    exp_count=len(experiments),
                                    xml_path=xml_path)
                self.add_message(code,description)
                
            if not should_be_in_xml and realpath in experiments:
                code="w012"
                description=hmm.get(code,
                                    context=self.context,
                                    exp_count=len(experiments),
                                    xml_path=xml_path,
                                    xml_context=context)
                self.add_message(code,description)    
                
    def scan_resource_limits_for_resource_xml(self,xml_path):
        
        root=self.maestro_experiment.get_interpreted_resource_lxml_element(xml_path)
        if root is None:
            return
        
        for batch in root.xpath("//BATCH"):
            queue=batch.attrib.get("queue")
            if not queue:
                continue
            system_limits=get_resource_limits_from_qstat_data(self.qstat_data,queue)
            batch_limits=get_resource_limits_from_batch_element(batch)
            
            """
            The dictionaries used here have more specific keys with units than
            the resource XMLs so less mistakes will be made. 
            This map helps convert them back.
            """
            key_to_attribute_name={"cpu_count":"cpu",
                                   "memory_bytes":"memory",
                                   "wallclock_seconds":"wallclock"}
            for key,attribute in key_to_attribute_name.items():
                value=batch_limits[key]
                xml_value=batch_limits[attribute]
                maximum=system_limits[key]
                
                if not maximum or value<=maximum:
                    continue
                code="e015"
                description=hmm.get(code,
                                    value=xml_value,
                                    attribute=attribute,
                                    maximum=maximum,
                                    xml_path=xml_path,
                                    queue=queue)
                self.add_message(code,description)
        
    def scan_resource_queues(self):
        """
        Scan queue usage from resource files.
        """
        
        if not self.qstat_data:
            logger.debug("Skipping resource queue scan, no qstat_data")
            return
        
        queues=sorted(list(self.qstat_data.keys()))
        
        "queues with a wallclock higher than allowed"
        for xml_path in self.resource_files:
            self.scan_resource_limits_for_resource_xml(xml_path)                    
        
        """
        Find queues that are used but do not exist in jobctl-qstat.
        
        Aliases are queues that do not show up in jobctl-qstat but
        they are still acceptable.
        """
        aliases=["xfer"]
        
        names=["FRONTEND_DEFAULT_Q",
               "FRONTEND_XFER_Q",
               "FRONTEND_DAEMON_Q",
               "BACKEND_DEFAULT_Q",
               "BACKEND_XFER_Q"]
        for name in names:
            value=self.maestro_experiment.get_resource_value_from_key(name)
            if value and value not in queues:
                code="b008" if value in aliases else "w010"
                description=hmm.get(code,
                                    value=value,
                                    name=name,
                                    queues=str(queues))
                self.add_message(code,description)
        
    def scan_config_files(self):
        for path in self.config_files:
            self.scan_config_file(path)
    
    def scan_config_file(self,path):
        "scan the content of config files (see scan_file_content for CSV content scan)"        
        
        key_values=file_cache.get_key_values_from_path(path)
        expected_config=EXPECTED_CONFIG_STATES.get(self.context,{})
        
        "find hard coded paths in pseudo-xml cfg variables"
        code="e010" if self.is_context_operational() else "w006"
        content=file_cache.open(path)
        data=get_weird_assignments_from_config_text(content)
        for section,d in data.items():
            for key,value in d.items():
                if value.startswith("/"):
                    description=hmm.get(code,
                                        config_path=path,
                                        bad_path=value)
                    self.add_message(code,description)
        
        "variables that should only be in experiment.cfg"
        if not path.endswith("experiment.cfg"):
            only_in_exp_config=["DISSEM_STATE","PREOP_STATE"]
            unexpected=[key for key in only_in_exp_config if key in key_values]
            if unexpected:
                code="w013"
                variables=", ".join(unexpected)
                description=hmm.get(code,
                                    cfg_path=path,
                                    variables=variables)
                self.add_message(code,description)
            
        "bad variable values"        
        for key,expected_value in expected_config.items():
            if key in key_values:
                value=key_values[key]
                if value != expected_value:
                    line="%s is '%s' not '%s'"%(key,value,expected_value)
                    unexpected.append(line)
        if unexpected:
            msg="\n".join(unexpected)
            if len(unexpected)>1:
                msg="\n"+msg
            code="e013"
            description=hmm.get(code,
                                context=self.context,
                                cfg_path=path,
                                unexpected=msg)
            self.add_message(code,description)
        
        commented_lines=get_commented_pseudo_xml_lines(content)
        if commented_lines:
            code="b007"
            description=hmm.get(code,
                                file_path=path,
                                count=len(commented_lines))
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
                code="e012"
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
                        code="w009"
                        description=hmm.get(code,
                                            maybe_typo=maybe_typo,
                                            expected=name)
                        self.add_message(code,description)
    
    
        for path in self.resource_files:            
            "unbalanced parentheses"
            code="e009"
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
                        code="b001"
                    else:
                        code="e011"
                    
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
            code="w005" if is_op else "i001"
            msg="\n".join(bad_links)
            if len(bad_links)>1:
                msg="\n"+msg
            description=hmm.get(code,
                                real_home=home_root,
                                bad_links=msg)
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
        
        content_without_comments=file_cache.open_without_comments(path)
        content_with_comments=file_cache.open(path)
        for check_data in self.filetype_to_check_datas[filetype]:
            
            content=content_without_comments if check_data["strip_comments"] else content_with_comments
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
                                    search=search.strip(),
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
                    code="e007"
                    kwargs["context"]=self.context
                else:
                    code="w001"
                
                description=hmm.get(code,**kwargs)
                self.add_message(code,description)
                
            elif node_type==NODE_TYPE.LOOP:
                code="w002"
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
            if result["signal"].startswith("$"):
                continue
            
            if result["signal"] not in NODELOGGER_SIGNALS:
                code="e006"
                description=hmm.get(code,
                                    bad_signal=result["signal"],
                                    line_number=result["line_number"],
                                    task_path=task_path)
                self.add_message(code,description)
        
    def scan_modules(self):
        """
        Scan the module folders, paths, and content in flow.xml files.
        """
        
        """
        This dictionary is necessary because 'modules/module1/flow.xml'
        may define '<MODULE name=module2>' at its root.      
        This dictionary has all aliases.
        
        Key is module name, value is real name.
        """
        source_to_target={}
        
        module_element_to_flow_path={}
        
        "key is MODULE element at root of a flow, value is flow xml path"
        root_module_to_flow_path={}
                
        for flow_path in self.flow_files:
            module_name=os.path.basename(os.path.dirname(flow_path))
            realname=os.path.basename(os.path.realpath(os.path.dirname(flow_path)))
            if realname!=module_name:
                source_to_target[module_name]=realname
            
            root=xml_cache.get(flow_path)
            modules=xml_cache.get_elements_of_tag(root,"MODULE")
            for m in modules:
                module_element_to_flow_path[m]=flow_path 
            if modules:
                root_module_to_flow_path[modules[0]]=flow_path
        
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
                code="e005"
                flow_xmls="\n".join(flow_paths)
                description=hmm.get(code,
                                    module_name=module_name,
                                    flow_xmls=flow_xmls)
                self.add_message(code,description)
        
        """
        find cases where the root element in modules/module1/flow.xml 
        defined module2, not module1
        """
        for element,path in root_module_to_flow_path.items():
            attribute_name=element.attrib.get("name")
            folder_name=os.path.basename(os.path.dirname(path))
            if attribute_name != folder_name:
                code="i002"
                description=hmm.get(code,
                                    folder_name=folder_name,
                                    xml_path=path,
                                    attribute_name=attribute_name)
                self.add_message(code,description)
                
        
    def scan_required_folders(self):        
        required_folders=("listings","sequencing","stats","logs")
        missing=[]
        for folder in required_folders:
            if not file_cache.isdir(self.path+folder):
                missing.append(folder)
        if missing:
            folders_msg=", ".join(missing)
            code="e001"
            description=hmm.get(code,folders=folders_msg)
            self.add_message(code,description)
        
    def scan_broken_symlinks(self):
        code="e004"
        broken=[path for path in self.files if file_cache.is_broken_symlink(path)]
        if broken:
            broken_links="\n".join(broken)
            description=hmm.get(code,broken_links=broken_links)
            self.add_message(code,description)
        
    def scan_node_names(self):
        code="e003"
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
                code="w008"
                description=hmm.get(code,
                                    xml_path=xml_path)
                self.add_message(code,description)
                             
        if support_status:
            
            "max length"
            max_chars=50
            if len(support_status)>max_chars:
                code="b002"
                description=hmm.get(code,
                                    xml_path=xml_path,
                                    char_count=len(support_status),
                                    max_chars=max_chars)
                self.add_message(code,description)
            
            "has url"
            if not url_regex.search(support_status):
                code="b003"
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
                code="b004"
                description=hmm.get(code,
                                    xml_path=xml_path,
                                    substrings=str(substrings))
                self.add_message(code,description)
                
        "no support status in op"
        is_op=self.is_context_operational()
        if not support_status and is_op:
            code="w007"
            description=hmm.get(code,
                                xml_path=xml_path)
            self.add_message(code,description)                
        
    def scan_xmls(self):
        code="e002"
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
            folders.update(get_ancestor_folders(folder,self.path))
            
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
        
        def sls(items):
            "sls is short for sorted, list, set"
            return sorted(list(set(items)))
        
        "all full paths to all files to scan"
        self.files=sls(paths)
        
        "all folders containing files to scan"
        self.folders=sls(folders)
        
        "all cfg files"
        self.config_files=sls(config_files)
        
        "all flow.xml files"
        self.flow_files=sls(flow_files)
        
        "all resource xml files"
        self.resource_files=sls(resource_files)
        
        "all tsk files"
        self.task_files=sls(task_files)
        
        "all xml files"
        self.xml_files=sls(xml_files)
    
    def get_report_text(self):
        lines=[]
        for m in self.messages:
            line="%s: %s\n%s"%(m["code"],m["label"],m["description"])
            lines.append(line)
        return "\n\n".join(lines)
    
    def print_report(self,
                     use_colors=True,
                     max_repeat=0,
                     level="b"):
        char_color_functions=OrderedDict([("c",print_red),
                                          ("e",print_orange),
                                          ("w",print_yellow),
                                          ("i",print_green),
                                          ("b",print_blue)])
        
        levels="cewib"
        if level not in levels:
            raise ValueError("Bad level '%s', but be one of '%s'"%(level,levels))
        
        "keep track of how many times we've shown each code"
        code_count={code:0 for code in self.codes}
        
        "key is first char of a code, value is how many we didn't show"
        hidden_code_counts_by_char={c:0 for c in levels}
        
        for c,f in char_color_functions.items():
            for message in self.messages:
                code=message["code"]
                
                if not code.startswith(c):
                    continue
                
                "do not print levels lower priority than the desired level"
                if levels.index(code[0]) > levels.index(level):
                    continue
                
                code_count[code]+=1
                if max_repeat and code_count[code]>max_repeat:
                    "already shown enough of this code, do not show"
                    hidden_code_counts_by_char[code[0]]+=1
                    continue
                
                f(code+": "+message["label"])
                print(message["description"])
        
        if max(hidden_code_counts_by_char.values()):
            msg="\nSkipped showing %s repeated codes: "%sum(hidden_code_counts_by_char.values())+"."
            for c in levels:
                count=hidden_code_counts_by_char[c]
                if count:
                    msg+="%s from code '%s', "%(count,c)
            print(msg[:-2])
        
        print("\nHeimdall found %s items to report for maestro suite:\n    %s"%(len(self.messages),self.path))
















