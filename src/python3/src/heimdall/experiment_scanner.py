import os.path
import re
from collections import OrderedDict
import Levenshtein

from constants import NODELOGGER_SIGNALS, SCANNER_CONTEXT, NODE_TYPE, HEIMDALL_CONTENT_CHECKS_CSV, EXPECTED_CONFIG_STATES, HUB_PAIRS, EXPERIMENT_LOG_FOLDERS, OPERATIONAL_USERNAME

from maestro_experiment import MaestroExperiment
from heimdall.file_cache import file_cache
from heimdall.message_manager import hmm
from home_logger import logger
from utilities.maestro import is_empty_module, get_weird_assignments_from_config_text, get_commented_pseudo_xml_lines
from utilities.heimdall.critical_errors import find_critical_errors
from utilities.heimdall.parsing import get_nodelogger_signals_from_task_path, get_levenshtein_pairs, get_resource_limits_from_batch_element
from utilities.heimdall.context import guess_scanner_context_from_path
from utilities.heimdall.path import get_ancestor_folders, is_editor_swapfile
from utilities.heimdall.git import scan_git_authors
from utilities import print_red, print_orange, print_yellow, print_green, print_blue, superstrip, remove_chars_in_text
from utilities import xml_cache, get_dictionary_list_from_csv, guess_user_home_from_path, get_links_source_and_target, iterative_deepening_search
from utilities.qstat import get_qstat_data_from_text, get_qstat_data, get_resource_limits_from_qstat_data
from utilities.shell import safe_check_output_with_status

"""
Matches codes like 'e001' and 'c010'
"""
CODE_REGEX = re.compile("[cewib][0-9]{3}")

"""
Matches executables that are named reasonbly, without characters like "+"
"""
EXECUTABLE_NAME_REGEX = re.compile("^[a-zA-Z0-9-_.]+$")


class ExperimentScanner():
    def __init__(self,
                 path,
                 context=None,
                 operational_home=None,
                 parallel_home=None,
                 critical_error_is_exception=True,
                 debug_qstat_output_override="",
                 debug_cmcconst_override="",
                 debug_op_username_override=""):

        if not path.endswith("/"):
            path += "/"

        self.path = path
        self.maestro_experiment = None
        self.codes = set()
        self.messages = []

        """
        Some scans like suite in the overview XML requires knowing the op/par home.
        Some scans may not care, so only throw a "does not exist" error
        if string has a value.
        """
        if operational_home and not os.path.exists(operational_home):
            raise ValueError("Home path for operational user does not exist: '%s'" % operational_home)
        if parallel_home and not os.path.exists(parallel_home):
            raise ValueError("Home path for parallel user does not exist: '%s'" % parallel_home)
        self.operational_home = operational_home
        self.parallel_home = parallel_home

        """
        Instead of running the qstat shell command, use this output instead.
        Useful for debugging/tests.
        """
        if debug_qstat_output_override:
            self.qstat_data = get_qstat_data_from_text(debug_qstat_output_override)
        else:
            self.qstat_data = get_qstat_data(timeout=3)
        
        """
        Instead of environment CMCCONST value, use this instead.
        Useful for debugging/tests.
        """
        if debug_cmcconst_override:
            os.environ["CMCCONST"]=debug_cmcconst_override
        
        """
        Instead of the operational username like 'smco500', use this instead.
        Useful for debugging/tests.
        """
        self.operational_username=debug_op_username_override if debug_op_username_override else OPERATIONAL_USERNAME
            
        critical_errors = find_critical_errors(path)
        for code, kwargs in critical_errors.items():
            self.add_message(code, **kwargs)
        if critical_errors:
            if critical_error_is_exception:
                raise ValueError("Experiment path:\n'%s'\nhas critical errors:\n%s" % (path, str(critical_errors)))
            return

        self.maestro_experiment = MaestroExperiment(path)

        self.index_experiment_files()

        if not context:
            context = guess_scanner_context_from_path(self.path)
        self.context = context

        self.scan_all_file_content()
        self.scan_all_task_content()
        self.scan_broken_symlinks()
        self.scan_config_files()
        self.scan_containers()
        self.scan_declared_files()
        self.scan_deprecated_files_folders()
        self.scan_exp_options()
        self.scan_extra_files()
        self.scan_file_permissions()
        self.scan_git_repo()
        self.scan_gitignore()
        self.scan_home_soft_links()
        self.scan_hub()
        self.scan_log_folder_permissions()
        self.scan_modules()
        self.scan_node_names()
        self.scan_operational_file_permissions()
        self.scan_overview_xmls()
        self.scan_required_files()
        self.scan_required_folders()
        self.scan_resource_files()
        self.scan_resource_queues()
        self.scan_root_links()
        self.scan_xmls()

        self.sort_messages()

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

        label = hmm.get_label(code)
        url = hmm.get_url(code)
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
            
    def scan_log_folder_permissions(self):        
        "log folders with inconsistent user/group/permissions"
        ugp_to_paths={}
        for folder in EXPERIMENT_LOG_FOLDERS:
            path=self.path+folder
            ugp=get_ugp_string(path)
            
            if not ugp:
                continue
            
            if ugp not in ugp_to_paths:
                ugp_to_paths[ugp]=[]
            ugp_to_paths[ugp].append(path)
            
        if len(ugp_to_paths)==1:
            return
        
        for ugp,paths in ugp_to_paths.items():
            for path in paths:
                self.add_message("e020",
                                 path=path,
                                 ugp=ugp,
                                 folders=", ".join(EXPERIMENT_LOG_FOLDERS))
    
    def scan_file_permissions(self):        
        "experiment files with inconsistent user/group/permissions"
        ugp_to_paths={}
        for path in self.files:
            ugp=get_ugp_string(path)
            
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
            if file_cache.can_user_write_to_path(self.operational_username,path):
                self.add_message("w023",
                                 user=self.operational_username,
                                 path=path)
    
    def scan_root_links(self):
        """
        recommend the creation of 'forecast' soft link for folders like 'e1'
        """
                
        links=get_links_source_and_target(self.path,max_depth=1)
        target_basenames=[os.path.basename(link["target"]) for link in links]
        source_basenames=[os.path.basename(link["source"]) for link in links]
        link_basenames=target_basenames+source_basenames
        
        r=re.compile("[a-z][0-9]")
        for folder in file_cache.listdir(self.path):
            if r.match(folder) and folder not in link_basenames:
                unclear=self.path+folder
                self.add_message("b013", unclear=unclear)
                
    def scan_gitignore(self):
        
        has_repo=file_cache.isdir(self.path+".git")
        if not has_repo:
            return
        
        gitignore_path=self.path+".gitignore"

        "no gitignore"
        if not file_cache.isfile(gitignore_path):
            self.add_message("w020", gitignore_path=gitignore_path)
            return
        
        content=file_cache.open(gitignore_path)
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

        must_have_repo = self.context in (SCANNER_CONTEXT.OPERATIONAL,
                                          SCANNER_CONTEXT.PREOPERATIONAL,
                                          SCANNER_CONTEXT.PARALLEL)
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
                line = "%s <%s>" % (author["name"], author["emails"][0])
                lines.append(line)
            dev_count = 5
            developers = "    "+"\n    ".join(lines[:dev_count])

            if developers:
                self.add_message("i006", developers=developers)

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
        maestro_files = self.task_files+self.config_files+self.resource_files+self.flow_files
        maestro_files = sorted(list(set(maestro_files)))
        explored = set()

        whitelist = [".gitignore"]

        for path in maestro_files:

            folder = os.path.dirname(path)
            if folder in explored:
                continue
            explored.add(folder)

            extra = []
            for basename in file_cache.listdir(folder):

                if basename in whitelist:
                    continue

                path = folder+"/"+basename
                if file_cache.isfile(path) and path not in maestro_files:
                    extra.append(path)

            if extra:
                filenames = "\n".join(extra)
                self.add_message("b006",
                                      folder=folder,
                                      filenames=filenames)

    def scan_hub(self):
        "scan links and targets of hub folder"

        hub_items = [self.path+"hub/"+filename for filename in file_cache.listdir(self.path+"hub")]

        "items in hub that are not links to folders"
        if self.context in (SCANNER_CONTEXT.OPERATIONAL,
                            SCANNER_CONTEXT.PREOPERATIONAL,
                            SCANNER_CONTEXT.PARALLEL):
            bad = []
            for path in hub_items:
                if not file_cache.islink(path):
                    bad.append(path)
            if bad:
                msg = "\n".join(bad)
                self.add_message("e014",
                                      context=self.context,
                                      bad=msg)
                
        "bad archive and protocol files"
        for path in self.hub_files:
            basename=os.path.basename(path)
            
            if basename==".protocole":
                self.add_message("b012", bad=path)
            
            if basename.startswith(".protocole_") or basename.startswith(".archive_monitor_"):
                if not file_cache.islink(path):
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
            if file_cache.exists(path1) and file_cache.exists(path2):
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
            if not file_cache.exists(path):
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

        realpath = file_cache.realpath(self.path)

        for context, xml_path in context_to_path.items():

            root = file_cache.etree_parse(xml_path)

            if root is None:
                """
                while it is a serious problem that the overview XML did not parse,
                it is not a problem belonging to the suite.            
                """
                return

            experiments = [file_cache.realpath(e.text) for e in root.xpath("//Exp")]
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

        self.non_standard_character_lines = []

        for path in self.config_files:
            self.scan_config_file(path)

        if self.non_standard_character_lines:
            details = "\n".join(self.non_standard_character_lines)
            self.add_message("b010",
                                  regex=EXECUTABLE_NAME_REGEX.pattern,
                                  details=details)

    def scan_config_file(self, path):
        "scan the content of config files (see scan_file_content for CSV content scan)"

        key_values = file_cache.get_key_values_from_path(path)
        expected_config = EXPECTED_CONFIG_STATES.get(self.context, {})

        "find hard coded paths in pseudo-xml cfg variables"
        code = "e010" if self.is_context_operational() else "w006"
        content = file_cache.open(path)
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

                name=get_equivalent_name_from_cfg_name(key)
                
                if not EXECUTABLE_NAME_REGEX.match(name):
                    line = "'%s' in '%s'" % (key, path)
                    if "$" in key:
                        line+" (excluding ${})"
                    self.non_standard_character_lines.append(line)

        "variables that should only be in experiment.cfg"
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

        commented_lines = get_commented_pseudo_xml_lines(content)
        if commented_lines:
            self.add_message("b007",
                                  file_path=path,
                                  count=len(commented_lines))

    def scan_resource_files(self):
        "scan the content of resource files (see scan_file_content for CSV content scan)"

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

        "resources.def variable name typo"
        standard_resource_defines = ["FRONTEND",
                                     "BACKEND",
                                     "FRONTEND_DEFAULT_Q",
                                     "FRONTEND_XFER_Q",
                                     "FRONTEND_DAEMON_Q",
                                     "BACKEND_DEFAULT_Q",
                                     "BACKEND_XFER_Q"]

        for name in standard_resource_defines:
            for path, declares in me.path_to_resource_declares.items():
                if name in declares:
                    continue
                for maybe_typo in declares:
                    d = Levenshtein.distance(name, maybe_typo)
                    if d == 1:
                        self.add_message("w009",
                                              maybe_typo=maybe_typo,
                                              expected=name)

        """
        this regex matches strings like:
            machine="${FRONTEND}"
        where:
            group 1 is attribute name
            group 2 is the value between double quotes.
        """
        attribute_regex = re.compile(r"""([a-zA-Z_]+)[ ]*=[ ]*["']([^'"]+)["']""")
        
        for path in self.resource_files:
            content = file_cache.open(path)
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
                    
        "DEPENDS_ON element"
        for path in self.resource_files:
            etree = file_cache.etree_parse(path)
            elements = etree.xpath("//DEPENDS_ON")
            for d_element in elements:

                "hard coded dependency experiment path"
                exp = d_element.get("exp")
                if exp and exp.startswith("/"):

                    if file_cache.isdir(exp):
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
            etree = file_cache.etree_parse(path)        
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
            

    def scan_home_soft_links(self):
        """
        Find core maestro files with a realpath outside the user home containing this project.
        """

        home_root = guess_user_home_from_path(self.path)
        bad_links = []

        for path in self.files:
            realpath = file_cache.realpath(path)
            if not realpath.startswith(home_root):
                bad_links.append(path)

        if bad_links:
            is_op = self.is_context_operational()
            code = "w005" if is_op else "i001"
            msg = "\n".join(bad_links)
            self.add_message(code,
                                  real_home=home_root,
                                  bad_links=msg)

    def scan_all_file_content(self):
        """
        See scan_file_content
        """
        self.parse_file_content_checks_csv()

        for path in self.files:
            self.scan_file_content(path)

    def scan_file_content(self, path):
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

        content_without_comments = file_cache.open_without_comments(path)
        content_with_comments = file_cache.open(path)
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
        cmcconst=os.path.realpath(os.environ.get("CMCCONST",""))
        if not cmcconst:
            return
        
        for path in self.declared_files:
            realpath=file_cache.realpath(path)
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

            if file_cache.exists(resource_path):
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

            elif node_type == NODE_TYPE.LOOP:
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
            self.add_message("i005", details="\n".join(msg_lines))
            
    def scan_containers(self):
        for container in self.maestro_experiment.container_elements:
            self.scan_container(container)
    
    def scan_container(self,container):
        container_name=container.attrib.get("name",container.tag)
        
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
        required_folders = EXPERIMENT_LOG_FOLDERS
        missing = []
        for folder in required_folders:
            if not file_cache.isdir(self.path+folder):
                missing.append(folder)
        if missing:
            folders_msg = ", ".join(missing)
            self.add_message("e001", folders=folders_msg)

    def scan_broken_symlinks(self):
        broken = [path for path in self.files if file_cache.is_broken_symlink(path)]
        if broken:
            self.add_message("e004",
                             broken_links="\n".join(broken))

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

        "multiple support info elements"
        root = file_cache.etree_parse(xml_path)
        if root is not None:
            support_infos = root.xpath("//SupportInfo")
            if len(support_infos) > 1:
                self.add_message("w008", xml_path=xml_path)

        if support_status:

            "max length"
            max_chars = 50
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
            substrings = ["Full", "Daytime", "Business", "Office", "None"]
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

    def scan_xmls(self):
        code = "e002"
        for path in self.xml_files:
            if file_cache.etree_parse(path) is None:
                self.add_message(code, xml=path)

        deprecated_attribute_xmls = []
        for path in self.flow_files:
            root = file_cache.etree_parse(path)
            if root is None:
                continue
            elements = root.xpath("//SUBMITS[@type]")
            if elements:
                deprecated_attribute_xmls.append(path)
        if deprecated_attribute_xmls:
            xml_paths="\n".join(deprecated_attribute_xmls)
            self.add_message("b009", xml_paths=xml_paths)

    def index_experiment_files(self):
        """
        Quickly find the path of all files that are in (or should be in)
        the maestro experiment repo: tsk, cfg, xml, and more.

        We cannot simply do a recursive search, because soft links sometimes
        lead to massive folders outside the experiment.
        """

        paths = set()
        folders = set()
        resource_files = set()
        flow_files = set()
        declared_files=set()
        rpath = self.path+"resources/"
        mpath = self.path+"modules/"

        "flow.xml files in modules folder"
        for folder in file_cache.listdir(mpath):
            flow = mpath+"flow.xml"
            if file_cache.isfile(flow):
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

                if not file_cache.isfile(path):
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
            if not file_cache.isdir(folder):
                continue
            for filename in file_cache.listdir(folder):
                path = folder+"/"+filename
                if file_cache.isfile(path) or file_cache.is_broken_symlink(path):
                    paths.add(path)

                    "also add resource XMLs that were not discovered by using the flow"
                    if path.startswith(rpath) and path.endswith(".xml"):
                        resource_files.add(path)
                        
        "index tsk cfg xml"
        task_files = []
        config_files = []
        xml_files = []
        for path in paths:
            if path.endswith(".tsk"):
                task_files.append(path)
            elif path.endswith(".cfg"):
                config_files.append(path)
            elif path.endswith(".xml"):
                xml_files.append(path)
        
        """
        hub files
        This search may be endless, so cut off the search after some time.
        """
        max_seconds=1
        hub_files=iterative_deepening_search(self.path+"hub",max_seconds)

        def sls(items):
            "sls is short for sorted, list, set"
            return sorted(list(set(items)))

        "all full paths to all files to scan"
        self.files = sls(paths)

        "all folders containing files to scan"
        self.folders = sls(folders)

        "all cfg files"
        self.config_files = sls(config_files)
        
        "all, or many hub files to some depth"
        self.hub_files = sls(hub_files)

        "all flow.xml files"
        self.flow_files = sls(flow_files)

        "all resource xml files"
        self.resource_files = sls(resource_files)

        "all tsk files"
        self.task_files = sls(task_files)

        "all xml files"
        self.xml_files = sls(xml_files)
        
        "all tsk, cfg, flow, xml files explicitly declared by the main flow"
        self.declared_files=sls(declared_files)

    def get_report_text(self):
        lines = []
        for m in self.messages:
            line = "%s: %s\n%s" % (m["code"], m["label"], m["description"])
            lines.append(line)
        return "\n\n".join(lines)

    def print_report(self,
                     use_colors=True,
                     max_repeat=0,
                     level="b",
                     whitelist=None,
                     blacklist=None):
        char_color_functions = OrderedDict([("c", print_red),
                                            ("e", print_orange),
                                            ("w", print_yellow),
                                            ("i", print_green),
                                            ("b", print_blue)])

        levels = "cewib"
        if level not in levels:
            raise ValueError("Bad level '%s', but be one of '%s'" % (level, levels))

        "keep track of how many times we've shown each code"
        code_count = {code: 0 for code in self.codes}

        "key is first char of a code, value is how many we didn't show"
        hidden_code_counts_by_char = {c: 0 for c in levels}

        for c, f in char_color_functions.items():
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

                f(code+": "+message["label"])
                print(message["description"])

        if max(hidden_code_counts_by_char.values()):
            msg = "\nSkipped showing %s codes because of repeat, whitelist, or blacklist: " % sum(hidden_code_counts_by_char.values())
            for c in levels:
                count = hidden_code_counts_by_char[c]
                if count:
                    msg += "%s from code '%s', " % (count, c)
            print(msg[:-2]+".")

        print("\nHeimdall found %s items to report for maestro suite:\n    %s" % (len(self.messages), self.path))

def strip_batch_variable(variable):
    """
    Given:
        $ABC
        ${ABC}
        XYZ
        $ABC$XYZ
    returns (stripped, is_one_variable):
        ABC, True
        ABC, True
        XYZ, False
        $ABC$XYZ, False
    """
    if not variable:
        return "",False
    
    is_one=False
    if variable.startswith("$") and variable.count("$")==1:
        is_one=True
        variable=superstrip(variable,"${}")
    return variable,is_one

def get_ugp_string(path):
    """
    Returns a string like:
        zulban:zulban:755
    for the user, group, and permissions of this file.
    """
    name,group,permissions,long_permissions=file_cache.get_user_group_permissions(path)
    if not name or not group or not permissions or not long_permissions:
        return ""
    return "%s:%s:%s"%(name,group,permissions)

BASH_VARIABLE_REGEX=re.compile("\\${[\\w]+}")
def get_equivalent_name_from_cfg_name(cfg_name):
    """
    Some source paths in CFG files may be complex.
    Given:
        folder1/file1${ABC}.sh
    basename is:
        file1a.sh
    which is useful for non-standard character verification.
    """
    
    basename=os.path.basename(cfg_name)
    
    if basename.endswith("/"):
        basename=basename[:-1]
        
    return BASH_VARIABLE_REGEX.sub("a",basename)
                
                