import os.path
import re
import Levenshtein
import json
import time
import copy
from datetime import datetime

from constants import NODELOGGER_SIGNALS, SCANNER_CONTEXT, NODE_TYPE, HEIMDALL_CONTENT_CHECKS_CSV, EXPECTED_CONFIG_STATES, HUB_PAIRS, EXPERIMENT_LOG_FOLDERS, REQUIRED_LOG_FOLDERS, OPERATIONAL_USERNAME, OLD_SEQ_VARIABLES, TASK_MAESTRO_BINS
from utilities.math import clamp

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import FileCache
from heimdall.message_manager import hmm
from home_logger import logger
from maestro import is_empty_module, get_weird_assignments_from_config_text, get_commented_pseudo_xml_lines, get_loop_indexes_from_expression, NodeLogParser, get_node_folder_from_node_path
from maestro.critical_errors import find_critical_errors
from heimdall.parsing import get_nodelogger_signals_from_task_path, get_levenshtein_pairs, get_resource_limits_from_batch_element, get_constant_definition_count, get_ssm_domains_from_string, get_etiket_variables_used_from_text, get_maestro_executables_from_bash_text, strip_batch_variable, replace_bash_variables
from heimdall.context import guess_scanner_context_from_path
from heimdall.path import get_ancestor_folders, is_editor_swapfile, is_parallel_path, DECENT_LINUX_PATH_REGEX_WITH_START_END, DECENT_LINUX_PATH_REGEX, DECENT_LINUX_PATH_REGEX_WITH_DOLLAR, get_latest_ssm_path_from_path, has_active_hcron_files
from heimdall.git import scan_git_authors
from heimdall.messages import print_scan_message
from heimdall.uspmadt import get_uspmadt_lines
from utilities.parsing import BASH_VARIABLE_DECLARE_REGEX
from utilities import print_red, print_orange, print_yellow, print_green, print_blue, superstrip
from utilities import xml_cache, get_dictionary_list_from_csv, guess_user_home_from_path, get_links_source_and_target, iterative_deepening_search, is_probably_compiled_executable, is_executable
from utilities.qstat import get_qstat_data_from_text, get_qstat_data, get_resource_limits_from_qstat_data
from utilities.shell import safe_check_output_with_status, get_git_remotes, get_all_repo_files, get_latest_hash_from_repo
from heimdall.language import get_language_from_environment

"""
Matches codes like 'e001' and 'c010'
"""
CODE_REGEX = re.compile("[cewib][0-9]{3}")

"""
Matches datestamp substring in suite paths like:
    /home/smco500/.suites/gdps_20200401/g1
but not:
    /home/smco500/.suites/gdps/g1
"""
DATESTAMP_PATH_REGEX = re.compile("_[0-9]{8}")

class ExperimentScanner():
    def __init__(self,
                 path,
                 context=None,
                 critical_error_is_exception=True,
                 debug_cmcconst_override="",
                 debug_op_username_override="",
                 debug_qstat_output_override="",
                 debug_hub_filecount=0,
                 debug_hub_ignore_age=False,
                 hub_seconds=1,
                 language=None,
                 operational_home=None,
                 operational_suites_home=None,
                 parallel_home=None,
                 write_results_json_path=""):

        logger.info("Starting ExperimentScanner for '%s'"%path)
        
        self.file_cache=FileCache()
            
        self.start_time=time.time()

        if not path.endswith("/"):
            path += "/"

        self.path = path
        self.maestro_experiment = None
        self.codes = set()
        self.messages = []
        self.hub_seconds=clamp(hub_seconds,1,600)
        
        self.debug_hub_filecount=debug_hub_filecount
        self.debug_hub_ignore_age=debug_hub_ignore_age
        
        if not language:
            language=get_language_from_environment()
        self.language=language

        """
        Some scans like suite in the overview XML requires knowing the op/par home.
        Some scans may not care, so only throw a "does not exist" error
        if string has a value.
        """
        if operational_home and not os.path.exists(operational_home):
            raise ValueError("Home path for operational user does not exist: '%s'" % operational_home)
        if parallel_home and not os.path.exists(parallel_home):
            raise ValueError("Home path for parallel user does not exist: '%s'" % parallel_home)
        if operational_suites_home and not os.path.exists(operational_suites_home):
            raise ValueError("Home path for operational suites owner does not exist: '%s'" % operational_suites_home)
        def append_slash_if_necessary(path):
            if not path:
                return path
            return path if path.endswith("/") else path+"/"
        self.operational_home = append_slash_if_necessary(operational_home)
        self.parallel_home = append_slash_if_necessary(parallel_home)
        self.operational_suites_home=append_slash_if_necessary(operational_suites_home)
        
        """
        If path is:
            /home/smco500/.suites/123
        home_root is guessed to be:
            /home/smco500
        """
        self.home_root = guess_user_home_from_path(self.path)

        """
        Instead of running the qstat shell command, use this output instead.
        Useful for debugging/tests.
        """
        self.debug_qstat_output_override=debug_qstat_output_override
        if debug_qstat_output_override:
            self.qstat_data = get_qstat_data_from_text(debug_qstat_output_override)
        else:
            self.qstat_data = get_qstat_data(timeout=3)
        
        """
        Instead of environment CMCCONST value, use this instead.
        Useful for debugging/tests.
        """
        self.debug_cmcconst_override=debug_cmcconst_override
        if debug_cmcconst_override:
            os.environ["CMCCONST"]=debug_cmcconst_override
        
        """
        Instead of the operational username like 'smco500', use this instead.
        Useful for debugging/tests.
        """
        self.operational_username=debug_op_username_override if debug_op_username_override else OPERATIONAL_USERNAME
        
        "guess context if necessary"        
        if not context:
            context = guess_scanner_context_from_path(self.path)
        self.context = context
        
        critical_errors = find_critical_errors(path)
        for code, kwargs in critical_errors.items():
            self.add_message(code, **kwargs)
        if critical_errors:
            self.set_results_json()
            if critical_error_is_exception:
                raise ValueError("Experiment path:\n'%s'\nhas critical errors:\n%s" % (path, str(critical_errors)))
            return

        self.maestro_experiment = MaestroExperiment(path)

        self.index_experiment_files()

        self.scan_all_file_content()
        self.scan_all_task_content()
        self.scan_bin_folder()
        self.scan_broken_symlinks()
        self.scan_config_files()
        self.scan_constant_redefines()
        self.scan_container_elements()
        self.scan_container_xml_files()
        self.scan_declared_files()
        self.scan_deprecated_files_folders()
        self.scan_dependencies()
        self.scan_etikets()
        self.scan_executables()
        self.scan_exp_options()
        self.scan_extra_files()
        self.scan_file_permissions()
        self.scan_git_repo()
        self.scan_gitignore()
        self.scan_external_soft_links()
        self.scan_hcrons()
        self.scan_hub()
        self.scan_hub_archiving()
        self.scan_identical_files()
        self.scan_install_soft_links()
        self.scan_log_folder_permissions()
        self.scan_modules()
        self.scan_node_names()
        self.scan_node_log()
        self.scan_operational_file_permissions()
        self.scan_overview_xmls()
        self.scan_readme_files()
        self.scan_required_files()
        self.scan_required_folders()
        self.scan_resource_definitions()
        self.scan_resource_xml_files()
        self.scan_resource_queues()
        self.scan_root_links()
        self.scan_shell_scripts()
        self.scan_ssm_uses()
        self.scan_unused_variables()
        self.scan_xmls()
        
        self.sort_messages()
        self.set_results_json()
        
        self.write_code_count_log()
        if write_results_json_path:
            self.write_results_json(write_results_json_path)
    
    def write_results_json(self, write_results_json_path):
        """
        Capture the full results and scan parameters in a JSON, and write to this path.
        """
        folder=os.path.dirname(write_results_json_path)
        if os.path.exists(folder) and not os.path.isdir(folder):
            raise ValueError("JSON results path exists but is not a folder: '%s'"%folder)
            
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        text=json.dumps(self.results_json,indent=4,sort_keys=True)
        with open(write_results_json_path,"w") as f:
            f.write(text)
        logger.info("Wrote full scan results JSON to file '%s'"%write_results_json_path)

        "log the scan parameters used"
        short_results_json=copy.copy(self.results_json)
        for key in ("messages","codes"):
            short_results_json.pop(key)
        parameters=json.dumps(short_results_json,indent=4,sort_keys=True)
        logger.info("Parameters used for the scan:\n"+parameters)
    
    def set_results_json(self):
                
        self.end_time=time.time()
        
        parameters={"path":self.path,
                    "hub_seconds":self.hub_seconds,
                    "debug_hub_filecount":self.debug_hub_filecount,
                    "debug_hub_ignore_age":self.debug_hub_ignore_age,
                    "debug_cmcconst_override":self.debug_cmcconst_override,
                    "has_debug_qstat_output_override":bool(self.debug_qstat_output_override),
                    "has_qstat_data":bool(self.qstat_data),
                    "language":self.language,
                    "operational_home":self.operational_home,
                    "parallel_home":self.parallel_home,
                    "operational_suites_home":self.operational_suites_home,
                    "home_root":self.home_root,
                    "operational_username":self.operational_username,
                    "context":self.context}
        
        seconds=self.end_time-self.start_time
        self.results_json={"messages":self.messages,
                           "codes":sorted(list(self.codes)),
                           "parameters":parameters,
                           "unix_start_time":self.start_time,
                           "unix_end_time":self.end_time,
                           "duration_seconds":seconds,
                           "USER":os.environ.get("USER",""),
                           "TRUE_HOST":os.environ.get("TRUE_HOST",""),
                           "commit_hash":get_latest_hash_from_repo(self.path)}
        
    def write_code_count_log(self):
        """
        Write a summary count of the scan codes found to the home log.
        This permits future audits of user homes to understand code frequencies.
        """
        
        code_count = {code: 0 for code in self.codes}
        for message in self.messages:
            code_count[message["code"]]+=1
        total=sum(code_count.values())
        
        line="Performed a scan on '%s' and found %s message codes: "%(self.path,total)
        line+=json.dumps(code_count,sort_keys=1)
        logger.info(line)

    def sort_messages(self):

        def sort_key(a):
            levels = "cewib"
            return str(levels.index(a["code"][0]))+a["code"][1:]

        self.messages = sorted(self.messages, key=sort_key)

    def is_context_operational(self):
        return self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                SCANNER_CONTEXT.PREOPERATIONAL)

    def is_context_monitored(self):
        return self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                SCANNER_CONTEXT.PREOPERATIONAL,
                                SCANNER_CONTEXT.PARALLEL)

    def is_non_operational_home(self,path):
        """
        Returns true if this path is within a non operational home, like a developer:
            /home/abc123/.suites/zdps
        These paths should not be referenced in operational projects.
        
        The path does not have to exist to return True.
        """
        
        if not path.startswith("/home/") and not path.startswith("/fs/home"):
            return False
        
        if os.path.exists(path):
            path=os.path.realpath(path)
        
        folders=[self.operational_home,self.parallel_home,self.operational_suites_home]
        for folder in folders:
            if folder and path.startswith(folder):
                return False
        return True

    def add_message(self, code, **kwargs):
        """
        Call this function when the scanner has detected a specific scenario.
        code is a message code like 'b001'.
        kwargs is all the curly bracket arguments found in the message_codes.csv file.
        If there is a missing or extra key in kwargs, raises an exception.
        This prevents showing the user messages with incomplete string insertions.
        """

        if not CODE_REGEX.match(code):
            raise ValueError("ExperimentScanner code '%s' does not match regex code regex:\n    %s" % (code, CODE_REGEX.pattern))

        label = hmm.get_label(code, language=self.language)
        url = hmm.get_url(code, language=self.language)
        if "language" not in kwargs:
            kwargs["language"]=self.language
        description = hmm.get(code,**kwargs)

        message = {"code": code, "label": label, "description": description, "url": url}
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

        path = HEIMDALL_CONTENT_CHECKS_CSV

        "filetype must be one of these"
        valid_filetypes = ["tsk", "cfg", "xml", "flow_xml", "resource_xml"]

        "list of check data, each row of CSV is a check data"
        self.file_content_checks = get_dictionary_list_from_csv(path)

        "key is filetype, value is list of check_data that apply to it"
        self.filetype_to_check_datas = {filetype: [] for filetype in valid_filetypes}

        for check_data in self.file_content_checks:
            if check_data["regex_string"]:
                try:
                    r = check_data["regex_string"]
                    check_data["regex"] = re.compile(r)
                except re.error:
                    raise ValueError("Bad regex string '%s' in file content CSV: '%s'" % (check_data["regex string"], path))

            if not check_data["regex_string"] and not check_data["substring"]:
                raise ValueError("All columns in file content CSV require either substring or regex string: '%s'" % path)

            check_data["strip_comments"] = check_data["strip_comments"] == "yes"

            filetypes = [i.strip() for i in check_data["filetypes"].split(",")]
            if "all" in filetypes:
                filetypes = valid_filetypes
            invalid = [i for i in filetypes if i not in valid_filetypes]
            if not filetypes or invalid:
                raise ValueError("Bad filetype arguments '%s' in file content CSV: '%s'" % (str(invalid), path))
            check_data["filetypes"] = filetypes

            for filetype in filetypes:
                self.filetype_to_check_datas[filetype].append(check_data)
    
    def scan_bin_folder(self):
        
        "find all bins in bin"
        folder=self.path+"bin/"
        if not os.path.exists(folder):
            return
        
        bins={}
        for filename in os.listdir(folder):
            path=folder+filename
            bins[filename]=path
        
        "find unused bins"
        unused=list(bins.keys())
        for path in self.task_files+self.config_files:
            if not unused:
                break
            
            for b in unused[:]:
                text=self.file_cache.open_without_comments(path)
                if b in text:
                    unused.remove(b)
        
        "any unused bins?"
        for b in unused:
            self.add_message("b032",path=bins[b])
    
    def scan_dependencies(self):
        me=self.maestro_experiment
        
        "key is experiment path, value is MaestroExperiment instance"
        me_cache={}
        
        """
        Many DEPENDS_ON lines may have the same exp/dep_name combination because of loop indexes.
        For w032 w033 w034 w035, each (exp,dep_name) combination should only trigger one code.
        This set tracks which have been visited:
            {(exp,dep_name), ...}
        """
        visited_exp_dep_names=set()
        
        for node_path,node_data in me.node_datas.items():
            dependencies=me.get_dependency_data_for_node_path(node_path)
            
            for dep_data in dependencies:
                
                visited_key=(dep_data["experiment_path"],dep_data["dep_name"])
                if visited_key in visited_exp_dep_names:
                    continue
                visited_exp_dep_names.add(visited_key)
            
                "is the node_path absolute, or relative"
                is_absolute=not dep_data["dep_name"].startswith(".")
                                
                "is the experiment this one (local) or external"
                is_local=not dep_data["experiment_path"]
                
                node_folder=get_node_folder_from_node_path(node_path)
                
                a=dep_data["node_path"]
                no_slash_node_path=a[1:] if a.startswith("/") else a
                dep_exists_locally=me.is_node_path(no_slash_node_path)
                
                if is_local and is_absolute and not dep_exists_locally:
                    self.add_message("w032",
                                     resource_path=node_data["resource_path"],
                                     node_path=dep_data["dep_name"])
                
                if is_local and not is_absolute and not dep_exists_locally:
                    self.add_message("w033",
                                     resource_path=node_data["resource_path"],
                                     dep_name=dep_data["dep_name"],
                                     node_path=dep_data["node_path"],
                                     node_folder=node_folder)
                
                
                if not is_local:
                    
                    path=dep_data["experiment_path"]
                                        
                    if path not in me_cache:
                        me_cache[path]=MaestroExperiment(path,
                                raise_exception_for_critical_errors=False)
                    external_me=me_cache[path]
                    
                    dep_exists_externally=external_me.is_node_path(no_slash_node_path)
                    
                    if not is_absolute:
                        self.add_message("e028",
                                         resource_path=node_data["resource_path"],
                                         dep_name=dep_data["dep_name"])
                    
                    if external_me.has_critical_errors:
                        self.add_message("w035",
                                         resource_path=node_data["resource_path"],
                                         exp=path)
                    elif not dep_exists_externally:
                        self.add_message("w034",
                                         resource_path=node_data["resource_path"],
                                         node_path=dep_data["node_path"],
                                         exp=path)
    
    def scan_executables(self):        
        for path in self.executable_files:
            if is_probably_compiled_executable(path):
                self.add_message("b031",path=path)
    
    def scan_shell_scripts(self):
        "run shell script syntax checks like 'bash -n' and 'ksh -n' on all tsk and cfg files."
        
        for path in self.task_files+self.config_files:
            content=self.file_cache.open(path)
            
            if "\n" not in content:
                continue
            
            """
            Identify shell interpreter.
            This may be difficult to get right, so take a guess.
            It's unclear to me whether the project files, maestro code, or 
            environment sets the shell interpreter for these files.
            """
            if content.startswith("#!"):
                first_line=content[:content.index("\n")]
                interpreter=first_line.split("/")[-1]
                if interpreter not in ["bash","ksh"]:
                    continue
            elif path.endswith(".cfg"):
                interpreter="ksh"
            else:
                interpreter="bash"
                
            verify_cmd=interpreter+" -n"
            cmd = verify_cmd+" "+path
            output,status=safe_check_output_with_status(cmd)
            if output:
                lines=output.split("\n")
                max_lines=10
                if len(lines)>max_lines:
                    last_line="... (%s more)"%(len(lines)-max_lines)
                    lines=lines[:max_lines]+[last_line]
                code="b026" if status==0 else "e027"
                trimmed_output="\n".join(lines).strip()
                self.add_message(code,
                                 path=path,
                                 verify_cmd=verify_cmd,
                                 output=trimmed_output)
                
    def scan_hcrons(self):
        "are there active hcrons for this suite"
        
        "if path is 502, look in 500 for hcrons"
        if self.home_root == self.operational_suites_home:
            hcron_folder=self.operational_home+".hcron"
        else:
            hcron_folder=self.home_root+".hcron"
            
        suite_name1=self.maestro_experiment.name.split("/")[-1]
        suite_name2=self.file_cache.realpath(self.path).split("/")[-1]
        
        for suite_name in (suite_name1,suite_name2):
            if has_active_hcron_files(hcron_folder,suite_name):
                return
        self.add_message("i010",
                         suite_name=suite_name,
                         hcron_folder=hcron_folder)
    
    def scan_unused_variables(self):        
        "find all variable defines in config files"
        
        defines=set()
        
        "key is bash variable name, path is list of config files where it is defined."
        variable_to_paths={}
        
        for path in self.config_files:
            values=self.file_cache.get_key_values_from_path(path)
            defines.update(values.keys())
            for variable in values:
                if variable not in variable_to_paths:
                    variable_to_paths[variable]=[]
                variable_to_paths[variable].append(path)
                
        "for each task and config file, remove used variables from 'unused'"
        unused=defines
        paths=self.config_files+self.task_files+self.resource_files
        for path in paths:
            variables=self.file_cache.get_bash_variables_used_in_path(path)
            unused=unused.difference(set(variables))
            
        "key is path to config file, value is list of variables it defines but which are unused"
        path_to_unused={}
        for variable in unused:
            for path in variable_to_paths[variable]:
                if path not in path_to_unused:
                    path_to_unused[path]=[]
                path_to_unused[path].append(variable)
                
        for path,variables in  path_to_unused.items():
            self.add_message("b024",
                             config=path,
                             unused=str(variables))
    
    def scan_etikets(self):        
        "find etikets defined in bad places"

        paths=self.task_files+self.config_files+[self.path+"experiment.cfg"]
        etikets_cfg_path=self.path+"etikets.cfg"
        
        "find etikets variable names used anywhere"
        etikets_used=[]
        for path in paths:
            text=self.file_cache.open_without_comments(path)
            etikets_used+=get_etiket_variables_used_from_text(text,require_etiket_programs=True)
        etikets_used=set(etikets_used)
        
        "find etikets defined outside etikets.cfg"
        for path in paths:
            values=self.file_cache.get_key_values_from_path(path)
            bad_etikets=set(values.keys()).intersection(etikets_used)
            bad_etikets=sorted(list(bad_etikets))
            if bad_etikets:
                self.add_message("b023",
                             etikets=str(bad_etikets),
                             good_path=etikets_cfg_path,
                             bad_path=path)
        
    def scan_readme_files(self):
        for path in self.readme_files:
            if path.endswith(".md"):
                continue
            
            suggested=os.path.basename(path)
            if "." in suggested:
                suggested=suggested.split(".")[0]
            suggested+=".md"
            
            self.add_message("b019",
                             readme=path,
                             suggested=suggested)
            
    def scan_log_folder_permissions(self):
        
        "lookup the user-group-permission (ugp) for the log paths"
        ugp_to_paths={}
        path_to_ugp={}
        for folder in EXPERIMENT_LOG_FOLDERS:
            path=self.path+folder
            ugp=self.file_cache.get_ugp_string(path)
            path_to_ugp[path]=ugp
            
            if not ugp:
                continue
            
            if ugp not in ugp_to_paths:
                ugp_to_paths[ugp]=[]
            ugp_to_paths[ugp].append(path)
            
        "log folders with inconsistent user/group/permissions"
        if len(ugp_to_paths)>1:
            for ugp,paths in ugp_to_paths.items():
                for path in paths:
                    self.add_message("e020",
                                     path=path,
                                     ugp=ugp,
                                     folders=", ".join(EXPERIMENT_LOG_FOLDERS))
        
        "op/preop/par log folders should be 775 or 755"
        if self.is_context_monitored():
            for path,ugp in path_to_ugp.items():
                expected="775"
                if expected not in ugp and "755" not in ugp:
                    self.add_message("e024",folder=path,expected=expected,ugp=ugp)                    
    
    def scan_file_permissions(self):        
        "experiment files with inconsistent user/group/permissions"
        ugp_to_paths={}
        for path in self.files:
            ugp=self.file_cache.get_ugp_string(path)
            
            if not ugp:
                continue
            
            if ugp not in ugp_to_paths:
                ugp_to_paths[ugp]=[]
            ugp_to_paths[ugp].append(path)
            
        if len(ugp_to_paths)==1:
            return
            
        highest=0
        most_common_ugp=None
        for ugp,paths in ugp_to_paths.items():
            if len(paths)>highest:
                highest=len(paths)
                most_common_ugp=ugp
        
        if not most_common_ugp:
            return
        
        for ugp,paths in ugp_to_paths.items():
            if ugp==most_common_ugp:
                continue
            for path in paths:
                self.add_message("b016",
                                 path=path,
                                 ugp=ugp,
                                 expected=most_common_ugp)
    
    def scan_operational_file_permissions(self):
        "operational users should not be able to overwrite their maestro files"
        
        if not self.is_context_operational():
            return
        
        for path in self.files:
            
            "The exp-catchup-icon in xflow requires that this file can be modified by the user"
            if path==self.path+"resources/catchup.xml":
                continue
            
            if self.file_cache.can_user_write_to_path(self.operational_username,path):
                self.add_message("w023",
                                 user=self.operational_username,
                                 path=path)
            
            owner,_,_,_=self.file_cache.get_user_group_permissions(path)
            expected="smco502"
            if expected != owner:
                self.add_message("w025",context=self.context,path=path,owner=owner,expected=expected)
                
    
    def scan_root_links(self):
        """
        recommend the creation of 'forecast' soft link for folders like 'e1'
        """
                
        links=get_links_source_and_target(self.path,max_depth=1)
        target_basenames=[os.path.basename(link["target"]) for link in links]
        source_basenames=[os.path.basename(link["source"]) for link in links]
        link_basenames=target_basenames+source_basenames
        
        r=re.compile("[a-z][0-9]")
        for folder in self.file_cache.listdir(self.path):
            if r.match(folder) and folder not in link_basenames:
                unclear=self.path+folder
                self.add_message("b013", unclear=unclear)
                
    def scan_gitignore(self):
        
        has_repo=self.file_cache.isdir(self.path+".git")
        if not has_repo:
            return
        
        gitignore_path=self.path+".gitignore"

        "no gitignore"
        if not self.file_cache.isfile(gitignore_path):
            self.add_message("w020", gitignore_path=gitignore_path)
            return
        
        content=self.file_cache.open(gitignore_path)
        lines=[line.strip() for line in content.split("\n") if line.strip()]            
        must_have=list(EXPERIMENT_LOG_FOLDERS)
        must_not_have=["hub","EntryModule","modules","flow.xml"]
        
        "gitignore must contain, and must not contain"
        for line in lines:
            if line in must_have:
                must_have.remove(line)
            
            for bad in must_not_have:
                if line==bad or line=="/"+bad:
                    self.add_message("w018",
                                          line=line,
                                          gitignore_path=gitignore_path)
        
        "required lines were not found"
        if must_have:
            content="'"+"', '".join(must_have)+"'"
            self.add_message("w019",
                                  content=content,
                                  gitignore_path=gitignore_path)

    def scan_git_repo(self):

        must_have_repo = self.is_context_monitored()
        must_be_clean = must_have_repo
        cmd = "cd %s ; git status --porcelain" % self.path
        output, status = safe_check_output_with_status(cmd)
        has_repo = status == 0
        
        "no repo"
        if must_have_repo and not has_repo:
            self.add_message("e016", context=self.context)

        "are there uncommited changes"
        if has_repo and output:
            if must_be_clean:
                code = "w015"
                kwargs={"context":self.context}
            else:
                code = "i004"
                kwargs={}
            self.add_message(code, **kwargs)

        if has_repo:
            lines = []
            include_current_branch=not self.is_context_monitored()
            authors = scan_git_authors(self.path,
                                       include_current_branch=include_current_branch)
            for author in authors:
                line=author["name"]
                if author["emails"]:
                    line+=" <%s>"%author["emails"][0]
                lines.append(line)
            dev_count = 5
            developers = "    "+"\n    ".join(lines[:dev_count])

            if authors:
                self.add_message("i006", developers=developers)
        
        "remote origin not gitlab"
        if has_repo:
            gitlab="git@gitlab.science.gc.ca"
            remotes=get_git_remotes(self.path)
            origin_fetch=remotes.get("origin",{}).get("fetch","")
            origin_push=remotes.get("origin",{}).get("push","")
            for origin in (origin_fetch,origin_push):
                if origin and not origin.startswith(gitlab):
                    self.add_message("b025",
                                     context=self.context,
                                     bad=origin,
                                     good=gitlab)
                    break

    def scan_extra_files(self):
        """
        Find extra files that probably don't belong in the project.
        """

        "text editor swap files"
        swaps = [path for path in self.files if is_editor_swapfile(path)]
        if swaps:
            filenames = "\n".join(swaps)
            self.add_message("i003", swaps=filenames)

        "Random files should not be adjacent to any maestro files like tsk, cfg, resource xml"
        maestro_files = self.task_files+self.config_files+self.resource_files+self.flow_files+self.internal_var_files+self.readme_files
        maestro_files = sorted(list(set(maestro_files)))
        explored = set()

        whitelist = [".gitignore",
                     self.path+"resources/resources.def"]

        for maestro_file in maestro_files:

            folder = os.path.dirname(maestro_file)
            if folder in explored:
                continue
            explored.add(folder)

            extra = []
            for basename in self.file_cache.listdir(folder):

                path = folder+"/"+basename
                
                if basename in whitelist or path in whitelist:
                    continue

                if self.file_cache.isfile(path) and path not in maestro_files:
                    extra.append(path)

            if extra:
                filenames = "\n".join(extra)
                self.add_message("b006",
                                 folder=folder,
                                 filenames=filenames)
                
    def scan_identical_files(self): 
        
        "key is md5sum string, value is list of paths with that sum"
        sums={}
        for path in self.files:
            if "/modules/" not in path:
                continue
            
            if self.file_cache.islink(path):
                continue
            
            md5=self.file_cache.md5(path)
            
            "empty file"
            if not md5:
                continue
            
            if md5 not in sums:
                sums[md5]=[]
                
            sums[md5].append(path)
        
        "for each folder in 'modules' find duplicate files"
        for md5,paths in sums.items():
            if len(paths)<2:
                continue
            
            """
            key is module name, a folder in 'modules'
            value is path to files in that folder with same md5
            """
            module_breakdown={}
            for path in paths:
                module_name=path.split("/modules/")[1].split("/")[0]
                if module_name not in module_breakdown:
                    module_breakdown[module_name]=[]
                module_breakdown[module_name].append(path)
            
            for module_name,paths in module_breakdown.items():
                if len(paths)>1:
                    self.add_message("b022",paths="\n".join(paths))
    
    def scan_hub_archiving(self):
        "find folders in hub with many files from many days, without archiving"
        
        many_files_threshold=1000 if not self.debug_hub_filecount else self.debug_hub_filecount
        many_days_threshold=7
        big_folders_with_no_archiving=[]
        
        "key is folder path, value is filecount"
        filecount={}
        for path in self.hub_files:
            folder=os.path.dirname(path)
            if folder not in filecount:
                filecount[folder]=0
            filecount[folder]+=1        
        
        for folder,count in filecount.items():
            paths=self.file_cache.listdir(folder)
            
            if len(paths)<many_files_threshold:
                continue
            
            protocole_files=[path for path in paths if path.startswith(".protocole_")]
            if protocole_files:
                continue
            
            "getting mtime for all would be slow, so get an evenly spread out sample"
            sample_count=20
            step=max(1,round(len(paths)/sample_count))
            datestamps=set()
            for index in range(0,len(paths),step):
                path=paths[index]
                try:
                    mtime=self.file_cache.get_mtime_from_path(path)
                except:
                    "in case the file has been deleted/moved since our scan"
                    continue
                date=datetime.utcfromtimestamp(mtime)
                datestamp=date.strftime("%Y-%m-%d")
                datestamps.add(datestamp)
            
            if len(datestamps)>=many_days_threshold or self.debug_hub_ignore_age:
                big_folders_with_no_archiving.append(folder)
        
        if big_folders_with_no_archiving:
            self.add_message("w036",
                             file_count=many_files_threshold,
                             day_count=many_days_threshold,
                             folders="\n".join(big_folders_with_no_archiving))
        
    def scan_hub(self):

        hub_items = [self.path+"hub/"+filename for filename in self.file_cache.listdir(self.path+"hub")]

        "items in hub that are not links to folders"
        if self.context in (SCANNER_CONTEXT.OPERATIONAL,
                            SCANNER_CONTEXT.PREOPERATIONAL,
                            SCANNER_CONTEXT.PARALLEL):
            bad = []
            for path in hub_items:
                if not self.file_cache.islink(path):
                    bad.append(path)
            if bad:
                msg = "\n".join(bad)
                self.add_message("e014",
                                      context=self.context,
                                      bad=msg)
        
        "deprecated products_dbase link"
        for path in hub_items:
            folder=path+"/products_dbase"
            if self.file_cache.exists(path) and self.file_cache.islink(path):
                self.add_message("b029",bad=folder)
        
        "bad archive and protocol files"
        for path in self.hub_files:
            basename=os.path.basename(path)
            
            if basename==".protocole":
                self.add_message("b012", bad=path)
            
            if basename.startswith(".protocole_") or basename.startswith(".archive_monitor_"):
                if not self.file_cache.islink(path):
                    self.add_message("w017", bad=path)
        
        """
        dissimilar targets
        for example eccc-ppp3 and eccc-ppp4 should have nearly identical targets
        """
        max_levenshtein_distance = 3
        hub = self.path+"hub/"
        source_and_target = get_links_source_and_target(hub)
        sources = [a["source"] for a in source_and_target]
        source_to_target = {a["source"]: a["target"] for a in source_and_target}
        "find pairs like eccc-ppp3 and eccc-ppp4"
        lev_data = get_levenshtein_pairs(sources)
        pairs = lev_data["pairs"]
        "find pairs like banting and daley"
        for item1, item2 in HUB_PAIRS:
            path1 = hub+item1
            path2 = hub+item2
            if self.file_cache.exists(path1) and self.file_cache.exists(path2):
                pairs.append([path1, path2])

        for item1, item2 in pairs:
            target1 = source_to_target[item1]
            target2 = source_to_target[item2]
            target_d = Levenshtein.distance(target1, target2)
            if target_d > max_levenshtein_distance:
                folder1 = os.path.basename(target1)
                folder2 = os.path.basename(target2)
                self.add_message("w014",
                                      folder1=folder1,
                                      folder2=folder2,
                                      target1=target1,
                                      target2=target2)

    def scan_deprecated_files_folders(self):
        old = ["hub/hare",
               "hub/brooks",
               "hub/eccc-ppp1",
               "hub/eccc-ppp2",
               "ExpDate",
               "ExpTimings",
               "flow.xml"]
        paths = [self.path+a for a in old]
        for path in paths:
            if not self.file_cache.exists(path):
                continue
            
            self.add_message("b005", path=path)

    def scan_overview_xmls(self):
        """
        Scan if this experiment is found in the correct or unexpected overview XMLs.
        """

        if not self.operational_home or not self.parallel_home:
            return

        context_to_path = {SCANNER_CONTEXT.OPERATIONAL: self.operational_home+"/xflow.suites.xml",
                           SCANNER_CONTEXT.PREOPERATIONAL: self.operational_home+"/xflow_preop.suites.xml",
                           SCANNER_CONTEXT.PARALLEL: self.parallel_home+"/xflow.suites.xml"}

        if self.context not in context_to_path:
            return

        realpath = self.file_cache.realpath(self.path)

        for context, xml_path in context_to_path.items():

            root = self.file_cache.etree_parse(xml_path)

            if root is None:
                """
                while it is a serious problem that the overview XML did not parse,
                it is not a problem belonging to the suite.            
                """
                return

            experiments = [self.file_cache.realpath(e.text) for e in root.xpath("//Exp")]
            should_be_in_xml = self.context == context

            if should_be_in_xml and realpath not in experiments:
                self.add_message("w011",
                                      context=self.context,
                                      exp_count=len(experiments),
                                      xml_path=xml_path)

            if not should_be_in_xml and realpath in experiments:
                self.add_message("w012",
                                      context=self.context,
                                      exp_count=len(experiments),
                                      xml_path=xml_path,
                                      xml_context=context)

    def scan_resource_limits_for_resource_xml(self, xml_path):

        root = self.maestro_experiment.get_interpreted_resource_lxml_element(xml_path)
        if root is None:
            return

        for batch in root.xpath("//BATCH"):
            queue = batch.attrib.get("queue")
            if not queue:
                continue
            system_limits = get_resource_limits_from_qstat_data(self.qstat_data, queue)
            batch_limits = get_resource_limits_from_batch_element(batch)

            """
            The dictionaries used here have more specific keys with units than
            the resource XMLs so less mistakes will be made. 
            This map helps convert them back.
            """
            key_to_attribute_name = {"cpu_count": "cpu",
                                     "memory_bytes": "memory",
                                     "wallclock_seconds": "wallclock"}
            for key, attribute in key_to_attribute_name.items():
                value = batch_limits[key]
                xml_value = batch_limits[attribute]
                maximum = system_limits[key]

                if not maximum or value <= maximum:
                    continue
                
                self.add_message("e015",
                                      value=xml_value,
                                      attribute=attribute,
                                      maximum=maximum,
                                      xml_path=xml_path,
                                      queue=queue)

    def scan_resource_queues(self):
        """
        Scan queue usage from resource files.
        """

        if not self.qstat_data:
            logger.debug("Skipping resource queue scan, no qstat_data")
            return

        queues = sorted(list(self.qstat_data.keys()))

        "queues with a wallclock higher than allowed"
        for xml_path in self.resource_files:
            self.scan_resource_limits_for_resource_xml(xml_path)

        """
        Find queues that are used but do not exist in jobctl-qstat.
        
        Aliases are queues that do not show up in jobctl-qstat but
        they are still acceptable.
        """
        aliases = ["xfer"]

        names = ["FRONTEND_DEFAULT_Q",
                 "FRONTEND_XFER_Q",
                 "FRONTEND_DAEMON_Q",
                 "BACKEND_DEFAULT_Q",
                 "BACKEND_XFER_Q"]
        for name in names:
            value = self.maestro_experiment.get_resource_value_from_key(name)
            if value and value not in queues:
                code = "b008" if value in aliases else "w010"
                self.add_message(code,
                                      value=value,
                                      name=name,
                                      queues=str(queues))

    def scan_config_files(self):
        for path in self.config_files:
            self.scan_config_file(path)

    def scan_config_file(self, path):
        "scan the content of config files (see scan_file_content for CSV content scan)"
        
        key_values = self.file_cache.get_key_values_from_path(path)
        expected_config = EXPECTED_CONFIG_STATES.get(self.context, {})

        "find hard coded paths in pseudo-xml cfg variables"
        code = "e010" if self.is_context_operational() else "w006"
        content = self.file_cache.open(path)
        weird_data = get_weird_assignments_from_config_text(content)
        for section, d in weird_data.items():
            for key, value in d.items():
                if value.startswith("/"):
                    self.add_message(code,
                                          config_path=path,
                                          bad_path=value)

        "find non-standard characters in names"
        for section, d in weird_data.items():
            for key, value in d.items():

                name=replace_bash_variables(key)
                
                if not DECENT_LINUX_PATH_REGEX_WITH_START_END.match(name):
                    dollar_msg="(using ${} is not what caused this error)" if "$" in key else ""
                    self.add_message("b010",
                                     bad=key,
                                     config_path=path,
                                     regex=DECENT_LINUX_PATH_REGEX_WITH_START_END.pattern,
                                     dollar_msg=dollar_msg)

        "variables that should only be in experiment.cfg"
        unexpected=[]
        if not path.endswith("experiment.cfg"):
            only_in_exp_config = ["DISSEM_STATE", "PREOP_STATE"]
            unexpected = [key for key in only_in_exp_config if key in key_values]
            if unexpected:
                variables = ", ".join(unexpected)
                self.add_message("w013",
                                      cfg_path=path,
                                      variables=variables)

        "bad variable values"
        for key, expected_value in expected_config.items():
            if key in key_values:
                value = key_values[key]
                if value != expected_value:
                    line = "%s is '%s' not '%s'" % (key, value, expected_value)
                    unexpected.append(line)
        if unexpected:
            msg = "\n".join(unexpected)
            self.add_message("e013",
                                  context=self.context,
                                  cfg_path=path,
                                  unexpected=msg)
            
        "commented code-like lines in pseudo xml"
        commented_lines = get_commented_pseudo_xml_lines(content)
        if commented_lines:
            self.add_message("b007",
                                  file_path=path,
                                  count=len(commented_lines))
            
        "hard coded paths instead of getdef"
        absolute_paths=[]
        for key,value in key_values.items():
            if value.startswith("/") and DECENT_LINUX_PATH_REGEX_WITH_DOLLAR.match(value):
                absolute_paths.append(value)
        if absolute_paths:
            self.add_message("b021",config=path,values="\n".join(absolute_paths))
            
        "absolute paths to developer paths/homes"
        non_op_homes=[a for a in absolute_paths if self.is_non_operational_home(a)]
        if non_op_homes:
            bad="\n".join(non_op_homes)
            if self.is_context_monitored():
                self.add_message("e025",context=self.context,path=path,bad=bad)
            else:
                self.add_message("i007",path=path,bad=bad)
        
    def scan_resource_definitions(self):
        "scan files like resources.def, overrides.def, etc"
        
        for path in self.maestro_experiment.resource_definition_paths:
            self.scan_resource_definition(path)
        
        resource_variables = ["FRONTEND",
                              "BACKEND",
                              "FRONTEND_DEFAULT_Q",
                              "FRONTEND_XFER_Q",
                              "FRONTEND_DAEMON_Q",
                              "BACKEND_DEFAULT_Q",
                              "BACKEND_XFER_Q"]
        
        "resources.def variable name typo"
        me=self.maestro_experiment
        for name in resource_variables:
            for path, declares in me.path_to_resource_declares.items():
                if name in declares:
                    continue
                for maybe_typo in declares:
                    d = Levenshtein.distance(name, maybe_typo)
                    if d == 1:
                        self.add_message("w009",
                                         maybe_typo=maybe_typo,
                                         expected=name)
                
        "required defines in resources.def"
        required=set(resource_variables)
        for path, declares in me.path_to_resource_declares.items():
            if not path.endswith("resources.def"):
                continue
            if not self.file_cache.exists(path):
                continue
            result=set(declares.keys())
            missing=required.difference(result)
            if missing:
                missing=sorted(list(missing))
                self.add_message("w031",
                                 path=path,
                                 required=sorted(list(required)),
                                 missing=missing)
    
    def scan_resource_definition(self,path):
        content=self.file_cache.open_without_comments(path)
        
        "find duplicate declares"
        lines=content.split("\n")
        variable_count={}
        for line in lines:
            match=BASH_VARIABLE_DECLARE_REGEX.match(line)
            if not match:
                continue
            name=match.group(1)
            if name not in variable_count:
                variable_count[name]=0
            variable_count[name]+=1        
        for variable,count in variable_count.items():
            if count>1:
                self.add_message("e021",variable=variable,path=path)
        
        "suite paths without datestamps"
        if self.is_context_monitored():
            variables=self.file_cache.get_key_values_from_path(path)
            not_datestamped=[]
            for name,value in variables.items():
                
                if not value.startswith("/"):
                    continue
                
                entry_module=value+"/EntryModule"
                is_experiment=self.file_cache.exists(entry_module)
                if not is_experiment:
                    continue
                
                if not DATESTAMP_PATH_REGEX.search(value):
                    not_datestamped.append(value)
            
            if not_datestamped:
                self.add_message("w028",
                                 resource_path=path,
                                 bad="\n".join(not_datestamped))
        
    def scan_resource_xml_files(self):
        "scan the content of resource XML files (see scan_file_content for CSV content scan)"

        me = self.maestro_experiment

        "undefined variables"
        d = me.undefined_resource_variables
        if d:
            for path, variables in d.items():
                self.add_message("e012",
                                 resource_path=path,
                                 variable_names=str(variables))

        "run_orji must be enabled"
        for path in self.resource_files:

            if not path.endswith("run_orji.xml"):
                continue

            data = self.maestro_experiment.get_batch_data_from_xml(path)
            try:
                catchup = int(data.get("catchup"))
            except:
                continue
            if catchup > 4:
                self.add_message("w016",
                                      resource_path=path,
                                      catchup=catchup)

        """
        this regex matches strings like:
            machine="${FRONTEND}"
        where:
            group 1 is attribute name
            group 2 is the value between double quotes.
        """
        attribute_regex = re.compile(r"""([a-zA-Z_]+)[ ]*=[ ]*["']([^'"]+)["']""")
        time_dependent_resources=[]
        for path in self.resource_files:
            content = self.file_cache.open(path)
            for match in attribute_regex.finditer(content):
                
                attribute_name = match.group(1)
                attribute_value = match.group(2)

                "unbalanced parentheses"                
                if attribute_value.count("{") != attribute_value.count("}"):
                    self.add_message("e009",
                                          attribute_value=attribute_value,
                                          file_path=path)

                "hard coded machine resource in operations"                    
                if (attribute_name == "machine" and 
                    not attribute_value.startswith("$") and
                    self.is_context_monitored()):
                    self.add_message("w022",
                                          context=self.context,
                                          machine_value=attribute_value,
                                          resource_path=path)
                
                "time dependent resources"
                if attribute_name in ("valid_hour","valid_dow"):
                    time_dependent_resources.append(path)
        if time_dependent_resources:
            time_dependent_resources=sorted(list(set(time_dependent_resources)))
            self.add_message("i009",
                             paths="\n".join(time_dependent_resources))
                    
        "DEPENDS_ON element"
        for path in self.resource_files:
            etree = self.file_cache.etree_parse(path)
            elements = etree.xpath("//DEPENDS_ON")
            for d_element in elements:

                "hard coded dependency experiment path"
                exp = d_element.get("exp")
                if exp and exp.startswith("/"):

                    if self.file_cache.isdir(exp):
                        code = "b001"
                    else:
                        code = "e011"

                    self.add_message(code,
                                          exp_value=exp,
                                          resource_path=path)
            
        "recommended bash variables used in BATCH attributes"
        recommended_variables={}
        recommended_variables["machine"]=["FRONTEND","BACKEND"]
        is_radar=os.path.basename(self.path).startswith("radar")
        if is_radar:
            recommended_variables["machine"]+=["RADAR_FRONTEND_HALL3",
                                            "RADAR_FRONTEND_HALL4"]
        recommended_variables["queue"]=["BACKEND_DEFAULT_Q",
                                     "BACKEND_XFER_Q",
                                     "FRONTEND_DAEMON_Q",
                                     "FRONTEND_DEFAULT_Q",
                                     "FRONTEND_HPNLS_Q",
                                     "FRONTEND_XFER_Q"]
        for path in self.resource_files:
            etree = self.file_cache.etree_parse(path)        
            batches = etree.xpath("//BATCH")
            for batch in batches:
                for attribute_name,variables in recommended_variables.items():
                    attribute_value=batch.attrib.get(attribute_name)
                    stripped_value,is_one_variable=strip_batch_variable(attribute_value)
                    recommended=sorted(recommended_variables[attribute_name])
                    if is_one_variable and stripped_value not in recommended:
                        self.add_message("b015",
                                         attribute_name=attribute_name,
                                         resource_path=path,
                                         attribute_value=attribute_value,
                                         recommended=", ".join(recommended))
    
    def scan_install_soft_links(self):        
        "is there a link on 500 pointing to 502"
        
        if not self.operational_suites_home:
            return
        
        realpath=self.file_cache.realpath(self.path)
        suites_realpath=self.file_cache.realpath(self.operational_suites_home)+"/.suites/"
        
        if not realpath or not suites_realpath:
            return
        
        if realpath.startswith(suites_realpath):
            no_slash=realpath[:-1] if realpath.endswith("/") else realpath
            expected=self.operational_home+"/.suites/"+os.path.basename(no_slash)
            if not self.file_cache.islink(expected):
                self.add_message("w029",
                                 target=self.path,
                                 source=expected)

    def scan_external_soft_links(self):
        """
        Find maestro files which are links to paths outside the project.
        """
        
        "find core maestro files with a realpath outside the user home containing this project."
        bad_links = []
        for path in self.files:
            realpath = self.file_cache.realpath(path)
            if not realpath.startswith(self.home_root):
                bad_links.append(path)
        if bad_links:
            is_op = self.is_context_operational()
            code = "w005" if is_op else "i001"
            msg = "\n".join(bad_links)
            self.add_message(code,
                                  real_home=self.home_root,
                                  bad_links=msg)
        
        "cases where realpath is okay, but within not linkchain"
        if self.is_context_operational():
            for path in self.files:
                "no need to report a complicated chain link if the realpath is simply wrong too, as above"
                if path in bad_links:
                    continue
                
                link_chain=self.file_cache.get_link_chain_from_link(path)
                for link_path in link_chain:
                    if link_path.startswith(self.home_root) or self.home_root.startswith(link_path):
                        continue
                    self.add_message("e026",
                                     context=self.context,
                                     path=path,
                                     bad="\n".join(link_chain))
                    break

    def scan_all_file_content(self):
        """
        See scan_file_content
        """
        self.parse_file_content_checks_csv()

        for path in self.files:
            self.scan_file_content_using_csv(path)
            self.scan_file_content(path)
            
    def scan_file_content(self,path):

        content_without_comments = self.file_cache.open_without_comments(path)
        
        "deprecated SEQ_ variables"
        for old,new in OLD_SEQ_VARIABLES.items():
            if old in content_without_comments:
                self.add_message("b017",old=old,new=new,path=path)
        
        "parallel content in operational"
        should_scan_paths=path in self.config_files or path in self.task_files or path in self.resource_files
        if should_scan_paths and self.is_context_operational():
            for match in DECENT_LINUX_PATH_REGEX.finditer(content_without_comments):
                path_string=match.group(0)
                par_string=is_parallel_path(path_string)
                if par_string:
                    self.add_message("w024",
                                     context=self.context,
                                     file_path=path,
                                     par_string=par_string)
        
    def scan_ssm_uses(self):
        
        "key is path to a file, value is list of SSM domains SSM used in that file"
        self.path_to_ssm_domains={}        
        for path in self.task_files+self.config_files:
            self.scan_ssm_uses_in_file(path)
                
        "key is domain, value is set of files that SSM use it"
        domain_to_paths={}
        "key is package, value is set of files that SSM use it"
        package_to_paths={}
        "key is package, value is set of domains"
        package_to_domains={}
        
        for path,domains in self.path_to_ssm_domains.items():
            
            domain_variables_without_ssm_prefix=[]
            
            for domain in domains:
                
                if domain.startswith("$") and not superstrip(domain,"${}").lower().startswith("ssm_"):
                    domain_variables_without_ssm_prefix.append(domain)
                
                if domain not in domain_to_paths:
                    domain_to_paths[domain]=set()
                domain_to_paths[domain].add(path)
                
                package=os.path.dirname(domain)
                if not package:
                    continue
                
                if package not in package_to_paths:
                    package_to_paths[package]=set()
                package_to_paths[package].add(path)
                
                if package not in package_to_domains:
                    package_to_domains[package]=set()
                package_to_domains[package].add(domain)
            
            if domain_variables_without_ssm_prefix:
                self.add_message("b030",
                                 path=path,
                                 variables="\n".join(domain_variables_without_ssm_prefix))
        
        "find cases where different versions of the same SSM are used"
        for package,domains in package_to_domains.items():
            if len(domains)<2:
                continue
            
            versions=sorted([os.path.basename(d) for d in package_to_domains[package]])
            paths="    "+"\n    ".join(package_to_paths[package])
            self.add_message("w027",
                             package=package,
                             versions=versions,
                             paths=paths)
    
    def scan_ssm_uses_in_file(self,path):
        
        content_without_comments = self.file_cache.open_without_comments(path)
        lines=content_without_comments.split("\n")
        domains=[]
        for line in lines:
            domains+=get_ssm_domains_from_string(line)
        
        self.path_to_ssm_domains[path]=domains
        
        for domain in domains:
            
            if not domain.startswith("/"):
                continue
            if "$" in domain:
                continue
            if self.file_cache.exists(domain):
                latest=get_latest_ssm_path_from_path(domain)
                if latest != domain:
                    self.add_message("i008",path=path,old=domain,new=latest)
        
            
    def scan_file_content_using_csv(self, path):
        """
        Use the file content CSV to scan for substrings and regexes in file content.

        This function only does generic content scans using the CSV, nothing specific
        to one code.
        """
        rpath = self.maestro_experiment.path+"resources/"
        filetype = None
        for extension in ("tsk", "cfg", "xml"):
            if path.endswith("."+extension):
                filetype = extension
                break
        if path.startswith(rpath) and path.endswith(".xml"):
            filetype = "resource_xml"
        if path.endswith("flow.xml"):
            filetype = "flow_xml"

        if not filetype:
            "files of unknown type are not content scanned"
            return

        content_without_comments = self.file_cache.open_without_comments(path)
        content_with_comments = self.file_cache.open(path)
        for check_data in self.filetype_to_check_datas[filetype]:

            content = content_without_comments if check_data["strip_comments"] else content_with_comments
            
            matching_strings=[]
            
            "find all strings that match either the regex or simple substring"
            
            found_substring = bool(check_data["substring"]) and check_data["substring"] in content
            if found_substring:
                matching_strings.append(check_data["substring"])            
            if check_data.get("regex"):
                matches=check_data.get("regex").finditer(content)
                for match in matches:
                    
                    """If there are regex groups (parentheses in the regex), 
                    use the first one. Otherwise, use the whole match.
                    """
                    if len(match.groups())>1:
                        matching_strings.append(match.group(1))
                    else:
                        matching_strings.append(match.group(0))                
            
            for matching_string in matching_strings:
                self.add_message(check_data["code"],
                                      matching_string=matching_string.strip(),
                                      file_path=path)
                
    def scan_declared_files(self):
        cmcconst=os.environ.get("CMCCONST","")
        if not cmcconst:
            return
        cmcconst=os.path.realpath(cmcconst)
        
        for path in self.declared_files:
            realpath=self.file_cache.realpath(path)
            if realpath.startswith(cmcconst):
                self.add_message("w021",
                                      path=path,
                                      cmcconst=cmcconst)

    def scan_required_files(self):

        is_op = self.is_context_operational()

        for node_path, node_data in self.maestro_experiment.node_datas.items():
            node_type = node_data["type"]
            resource_path = node_data["resource_path"]
            task_path = node_data["task_path"]

            if self.file_cache.exists(resource_path):
                continue

            if node_type == NODE_TYPE.TASK:
                kwargs = {"task_path": task_path,
                          "resource_path": resource_path}

                if is_op:
                    code = "e007"
                    kwargs["context"] = self.context
                else:
                    code = "w001"

                self.add_message(code, **kwargs)

            elif node_type in (NODE_TYPE.LOOP, NODE_TYPE.SWITCH):
                self.add_message("w002",
                                      node_path=node_path,
                                      resource_path=resource_path)

    def scan_all_task_content(self):
        for task_path in self.task_files:
            self.scan_task(task_path)

    def scan_task(self, task_path):
        "find invalid nodelogger signals"
        results = get_nodelogger_signals_from_task_path(task_path)
        msg_lines = []
        for result in results:
            if result["signal"].startswith("$"):
                continue

            if result["signal"] not in NODELOGGER_SIGNALS:
                line = "Signal '%s' in line %s of file '%s'" % (result["signal"],
                                                                result["line_number"],
                                                                task_path)
                msg_lines.append(line)

        if msg_lines:
            self.add_message("i005", 
                             details="\n".join(msg_lines),
                             signals=str(NODELOGGER_SIGNALS))
        
        "maestro executables in task files without $SEQ_BIN prefix"
        content=self.file_cache.open_without_comments(task_path)
        executables=get_maestro_executables_from_bash_text(content)
        prefix1="SEQ_BIN"
        prefix2="MAESTRO_BIN"
        for executable_path in executables:
            basename=os.path.basename(executable_path)
            dirname=os.path.dirname(executable_path)
            if basename not in TASK_MAESTRO_BINS:
                continue
            stripped=superstrip(dirname,"${}")
            if stripped in (prefix1,prefix2):
                continue
            expected="${SEQ_BIN}/"+basename
            self.add_message("b027",
                             cmd=executable_path,
                             path=task_path,
                             tool=basename,
                             prefix1=prefix1,
                             prefix2=prefix2,
                             expected=expected)
            
    def scan_container_xml_files(self):
        for path in self.container_xml_files:
            self.scan_container_xml_file(path)
    
    def scan_container_xml_file(self,path):
        root=self.file_cache.etree_parse(path)
        
        "lxml is silly and prints a warning to stdout unless the check is done this way"
        if not (root is not None):
            return
        
        loop_elements=root.xpath("//LOOP")
        for loop_element in loop_elements:
            expression=loop_element.attrib.get("expression")
            if not expression:
                continue
            result=get_loop_indexes_from_expression(expression)
            if not result:
                self.add_message("e023",path=path,loop_expression=expression)
    
    def scan_container_elements(self):
        for container in self.maestro_experiment.container_elements:
            self.scan_container_element(container)
    
    def scan_container_element(self,container):
        container_name=container.attrib.get("name",container.tag)
        
        "loop expressions"
        
        "find children in containers with duplicate name/subname"
        names=[]
        subnames=[]
        duplicates=[]
        
        for child in container.getchildren():
            name=child.attrib.get("name","")
            if name in names:
                duplicates.append(name)
            if name:
                names.append(name)
                
            subname=child.attrib.get("sub_name","")
            if subname in subnames:
                duplicates.append(name)
            if subname:
                subnames.append(subname)
        
        duplicates=sorted(list(set(duplicates)))
        for d in duplicates:
            self.add_message("e017",
                                  container_name=container_name,
                                  duplicate_name=d)

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
        source_to_target = {}

        module_element_to_flow_path = {}
        
        "EntryModule target basename is 'main' "
        entry_module=self.path+"EntryModule"
        target=os.path.realpath(entry_module)
        basename=os.path.basename(target)
        good="main"
        if basename != good:
            self.add_message("b028",
                             path=entry_module,
                             good=good,
                             bad=basename)

        "key is MODULE element at root of a flow, value is flow xml path"
        root_module_to_flow_path = {}

        for flow_path in self.flow_files:
            module_name = os.path.basename(os.path.dirname(flow_path))
            realname = os.path.basename(os.path.realpath(os.path.dirname(flow_path)))
            if realname != module_name:
                source_to_target[module_name] = realname

            root = xml_cache.get(flow_path)
            modules = xml_cache.get_elements_of_tag(root, "MODULE")
            for m in modules:
                module_element_to_flow_path[m] = flow_path
            if modules:
                root_module_to_flow_path[modules[0]] = flow_path

        not_empty_modules = [m for m in module_element_to_flow_path if not is_empty_module(m)]

        """
        key is module realname
        value is list of flow.xml paths defining this module, if the
        list length is greater than 1 our module is scatterd
        """
        module_declares = {}

        for m in not_empty_modules:
            module_name = m.attrib.get("name")
            if not module_name:
                continue

            realname = source_to_target.get(module_name, module_name)
            if realname not in module_declares:
                module_declares[realname] = []
            flow_path = module_element_to_flow_path[m]
            module_declares[realname].append(flow_path)

        for module_name, flow_paths in module_declares.items():
            if len(flow_paths) > 1:
                flow_xmls = "\n".join(flow_paths)
                self.add_message("e005",
                                      module_name=module_name,
                                      flow_xmls=flow_xmls)

        """
        find cases where the root element in modules/module1/flow.xml 
        defined module2, not module1
        """
        for element, path in root_module_to_flow_path.items():
            attribute_name = element.attrib.get("name")
            folder_name = os.path.basename(os.path.dirname(path))
            if attribute_name != folder_name:
                self.add_message("i002",
                                      folder_name=folder_name,
                                      xml_path=path,
                                      attribute_name=attribute_name)

    def scan_required_folders(self):
        missing = []
        for folder in REQUIRED_LOG_FOLDERS:
            if not self.file_cache.isdir(self.path+folder):
                missing.append(folder)
        if missing:
            folders_msg = ", ".join(missing)
            self.add_message("e001", folders=folders_msg)
        
        me=self.maestro_experiment
        value1=me.get_resource_value_from_key("SEQ_RUN_STATS_ON")
        value2=me.get_resource_value_from_key("SEQ_AVERAGE_WINDOW")
        is_stats_required=value1 or value2
        folder=self.path+"stats"
        if is_stats_required and not self.file_cache.isdir(folder):
            self.add_message("e022", required=folder)

    def scan_broken_symlinks(self):
        for path in self.files:
            if self.file_cache.is_broken_symlink(path):
                self.add_message("e004",
                                 link=path)

    def scan_node_log(self):
        me=self.maestro_experiment
        
        latest_nodelog=me.get_latest_node_log()
        if not latest_nodelog:
            return
        nlp=NodeLogParser(me.get_latest_node_log())
        
        "wallclock too big, based on nodelog"
        threshold_factor=5
        minimum_wallclock_seconds=30
        for node_path,node_data in me.node_datas.items():
            latest_success_seconds=nlp.get_successful_execution_duration(node_path)
            if not latest_success_seconds:
                continue
            
            rpath=node_data["resource_path"]
            data = me.get_batch_data_from_xml(rpath)
            if not data:
                continue
            
            try:
                wallclock_seconds=int(data.get("wallclock",0))
            except ValueError:
                continue
            if not wallclock_seconds:
                continue
            
            if wallclock_seconds < minimum_wallclock_seconds:
                continue
            
            if wallclock_seconds>latest_success_seconds*threshold_factor:
                timestamp=nlp.latest_execution_timestamp.get(node_path,"unknown")
                factor=round(wallclock_seconds/latest_success_seconds,2)
                self.add_message("w026",
                                 node_path=node_path,
                                 wallclock_seconds=wallclock_seconds,
                                 resource_xml=rpath,
                                 datestamp=timestamp,
                                 latest_seconds=latest_success_seconds,
                                 factor=factor,
                                 threshold=threshold_factor)

    def scan_node_names(self):        
        required_regex = re.compile(r"^(?i)[a-z](?:[a-z0-9]+[._-]?)*[a-z0-9]+$")
        recommended_regex = re.compile(r"^(?i)[a-z](?:[a-z0-9]+[._]?)*[a-z0-9]+$")
        
        for node_path in self.maestro_experiment.get_node_paths():
            node_data=self.maestro_experiment.get_node_data(node_path)
            
            """
            switch items which have names like '00' and '12'
            can be ignored in this check, as they are only used internally.
            """
            if node_data["type"] == NODE_TYPE.SWITCH_ITEM:
                continue
            
            flow_path=node_data["flow_path"]
            node_name = node_path.split("/")[-1]
            
            if required_regex.match(node_name):
                if not recommended_regex.match(node_name):
                    self.add_message("b014", 
                                     node_name=node_name,
                                     flow_path=flow_path,
                                     regex=recommended_regex.pattern)
            else:
                self.add_message("e003",
                                 node_name=node_name,
                                 flow_path=flow_path,
                                 regex=required_regex.pattern)

    def scan_exp_options(self):
        xml_path = self.maestro_experiment.path+"ExpOptions.xml"
        support_status = self.maestro_experiment.get_support_status()
        url_regex = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

        "multiple support info elements in the same parent element"
        root = self.file_cache.etree_parse(xml_path)
        if root is not None:
            support_infos = root.xpath("//SupportInfo")
            parents=[e.getparent() for e in support_infos]
            if len(parents) != len(set(parents)):
                self.add_message("w008", xml_path=xml_path)

        if support_status:

            "max length"
            max_chars = 150
            if len(support_status) > max_chars:
                self.add_message("b002",
                                 xml_path=xml_path,
                                 char_count=len(support_status),
                                 max_chars=max_chars)

            "has url"
            if not url_regex.search(support_status):
                self.add_message("b003", xml_path=xml_path)

            "reasonable start string like 'full support' "
            found_substring = False
            stripped_status = re.sub("[ -_]+", "", support_status.lower())
            substrings = ["Full", "Daytime", "Business", "Office", "None", "Experiment"]
            for substring in substrings:
                if stripped_status.startswith(substring.lower()):
                    found_substring = True
                    break
            if not found_substring:
                self.add_message("b004", 
                                 xml_path=xml_path, 
                                 substrings=str(substrings))

        "no support status in op"
        is_op = self.is_context_operational()
        if not support_status and is_op:
            self.add_message("w007", xml_path=xml_path)
    
    def scan_constant_redefines(self):
        """
        Look at bash-like files (tsk, cfg) for variable definition issues.
        """
        for node_path, node_data in self.maestro_experiment.node_datas.items():
            task_path = node_data["task_path"]
            config_path = node_data["config_path"]
            for path in (task_path,config_path):
                self.scan_constant_redefine(path)

    def scan_constant_redefine(self, path):
        """
        Look at a bash-like file (tsk, cfg) for variable definition issues.
        """
        content_without_comments = self.file_cache.open_without_comments(path)
        constants=get_constant_definition_count(content_without_comments)
        for variable,count in constants.items():
            if count>1:
                self.add_message("b018", variable=variable,path=path)

    def scan_xmls(self):
        code = "e002"
        for path in self.xml_files:
            if self.file_cache.etree_parse(path) is None:
                self.add_message(code, xml=path)

        deprecated_attribute_xmls = []
        for path in self.flow_files:
            root = self.file_cache.etree_parse(path)
            if root is None:
                continue
            elements = root.xpath("//SUBMITS[@type]")
            if elements:
                deprecated_attribute_xmls.append(path)
        for xml_path in deprecated_attribute_xmls:
            self.add_message("b009", xml_path=xml_path)

    def index_experiment_files(self):
        """
        Quickly find the path of all files that are in (or should be in)
        the maestro experiment repo: tsk, cfg, xml, and more.

        We cannot simply do a recursive search, because soft links sometimes
        lead to massive folders outside the experiment.
        """

        paths = set(get_all_repo_files(self.path))
        folders = set()
        resource_files = set()
        flow_files = set()
        declared_files=set()
        executable_files=set()
        rpath = self.path+"resources/"
        mpath = self.path+"modules/"
                
        "full path to all folders in the 'modules' folder"
        self.module_folders=[f for f in self.file_cache.listdir(mpath) if self.file_cache.isdir(f)]

        "flow.xml files in modules folder"
        for folder in self.module_folders:
            flow = mpath+"flow.xml"
            if self.file_cache.isfile(flow):
                paths.add(flow)
                flow_files.add(flow)
                declared_files.add(flow)        

        "find maestro files discovered through flow.xml"
        for node_path in self.maestro_experiment.get_node_datas():
            for prefix in ("task", "resource", "config", "flow"):
                path = node_path[prefix+"_path"]
                if not path:
                    continue
                folder = os.path.dirname(path)
                folders.add(folder)

                if not self.file_cache.isfile(path):
                    continue
                paths.add(path)
                declared_files.add(path)
                if prefix == "resource":
                    resource_files.add(path)
                elif prefix == "flow":
                    flow_files.add(path)

        "also add parent folders of all folders, as long as they are in the experiment"
        for folder in list(folders):
            folders.update(get_ancestor_folders(folder, self.path))

        "find maestro files (including broken symlinks) not in flow.xml, but in the same folders"
        for folder in folders:
            if not self.file_cache.isdir(folder):
                continue
            for filename in self.file_cache.listdir(folder):
                path = folder+"/"+filename
                if self.file_cache.isfile(path) or self.file_cache.is_broken_symlink(path):
                    paths.add(path)

                    "also add resource XMLs that were not discovered by using the flow"
                    if path.startswith(rpath) and path.endswith(".xml"):
                        resource_files.add(path)
        
        """
        Other files at the root of a module folder.
        Like README, internal.var
        """
        internal_var_files=[]
        readme_files=[]
        module_folder=self.path+"modules/"
        def is_readme(basename):
            return basename.lower().startswith("readme")
        for subfolder in self.file_cache.listdir(module_folder):
            path=module_folder+subfolder+"/internal.var"
            if self.file_cache.exists(path):
                internal_var_files.append(path)
            
            for basename in self.file_cache.listdir(module_folder+subfolder):
                path=module_folder+subfolder+"/"+basename
                if is_readme(basename) and self.file_cache.isfile(path):                    
                    readme_files.append(path)
        for basename in self.file_cache.listdir(self.path):
            if is_readme(basename):
                readme_files.append(self.path+basename)
                
        "index tsk cfg xml links"
        task_files = []
        config_files = []
        xml_files = []
        container_xml_files = []
        links = []
        for path in paths:
            if self.file_cache.islink(path):
                links.append(path)
            
            if path.endswith(".tsk"):
                task_files.append(path)
            elif path.endswith(".cfg"):
                config_files.append(path)
            elif path.endswith(".xml"):
                xml_files.append(path)
                if path.endswith("container.xml"):
                    container_xml_files.append(path)
        
        """
        hub files
        This search may be endless, so cut off the search after some time.
        """
        hub_files=iterative_deepening_search(self.path+"hub",self.hub_seconds)
        
        executable_files=[path for path in set(paths) if is_executable(path)]
        
        def sls(items):
            "sls is short for sorted, list, set"
            return sorted(list(set(items)))

        "all full paths to all files to scan"
        self.files = sls(paths)
        
        "all file or folder symlinks"
        self.links = sls(links)

        "all folders containing files to scan"
        self.folders = sls(folders)

        "all cfg files"
        self.config_files = sls(config_files)
        
        "all container.xml files"
        self.container_xml_files = sls(container_xml_files)
        
        "all tsk, cfg, flow, xml files explicitly declared by the main flow"
        self.declared_files=sls(declared_files)
        
        "all, or many hub files to some depth"
        self.hub_files = sls(hub_files)

        "all flow.xml files"
        self.flow_files = sls(flow_files)
        
        "all internal.var files"
        self.internal_var_files=sls(internal_var_files)
        
        "all readme files"
        self.readme_files=sls(readme_files)

        "all resource xml files"
        self.resource_files = sls(resource_files)

        "all tsk files"
        self.task_files = sls(task_files)

        "all xml files"
        self.xml_files = sls(xml_files)
        
        "all files with 'x' permission"
        self.executable_files=executable_files

    def get_report_text(self,
                        max_repeat=0):
        lines = []
        shown_code_count={}
        for m in self.messages:
            
            code=m["code"]
            if code not in shown_code_count:
                shown_code_count[code]=0
            shown_code_count[code]+=1
            if max_repeat and shown_code_count[code]>max_repeat:
                continue
            
            line = "%s: %s\n%s" % (m["code"], m["label"], m["description"])
            lines.append(line)
        return "\n\n".join(lines)

    def print_report(self,
                     use_colors=True,
                     max_repeat=0,
                     level="b",
                     whitelist=None,
                     blacklist=None):

        levels = "cewib"
        if level not in levels:
            raise ValueError("Bad level '%s', must be one of '%s'" % (level, levels))

        "keep track of how many times we've shown each code"
        code_count = {code: 0 for code in self.codes}

        "key is first char of a code, value is how many we didn't show"
        hidden_code_counts_by_char = {c: 0 for c in levels}

        for c in levels:
            for message in self.messages:
                code = message["code"]

                if not code.startswith(c):
                    continue

                "do not print levels lower priority than the desired level"
                if levels.index(code[0]) > levels.index(level):
                    continue
                
                code_count[code] += 1
                if max_repeat and code_count[code] > max_repeat:
                    "already shown enough of this code, do not show"
                    hidden_code_counts_by_char[code[0]] += 1
                    continue

                if whitelist and code not in whitelist:
                    hidden_code_counts_by_char[code[0]] += 1
                    continue

                if blacklist and code in blacklist:
                    hidden_code_counts_by_char[code[0]] += 1
                    continue
                
                print_scan_message(message)

        if max(hidden_code_counts_by_char.values()):
            msg = "\nSkipped showing %s codes because of repeat, whitelist, or blacklist: " % sum(hidden_code_counts_by_char.values())
            for c in levels:
                count = hidden_code_counts_by_char[c]
                if count:
                    msg += "%s from code '%s', " % (count, c)
            print(msg[:-2]+".")

        print("\nHeimdall found %s items to report for maestro suite:\n    %s" % (len(self.messages), self.path))


                