[(Français)](../fr/heimdall_codes.md)

# Heimdall Message Codes

This page lists all Heimdall codes and messages. See also the [Heimdall README](https://gitlab.science.gc.ca/CMOI/maestro/blob/integration/src/python3/HEIMDALL.md).




# Level: Critical
![color c image](../color-critical.png)

### [c001](#c001): No EntryModule

EntryModule link does not exist: '{entry_module}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c002](#c002): Bad EntryModule

EntryModule is not a link: '{entry_module}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c003](#c003): No experiment here

Could not find an experiment for path: '{path}'. A valid experiment folder contains an 'EntryModule' link.


[More info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c004](#c004): No EntryModule flow.xml

The required EntryModule flow.xml file does not exist: '{flow_xml}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c005](#c005): Bad EntryModule flow.xml

The required EntryModule flow.xml file failed to parse as XML: '{flow_xml}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

# Level: Error
![color e image](../color-error.png)

### [e001](#e001): Missing suite folders

All suites require the folders: 'listings', 'sequencing', and 'logs'. This suite is missing: {folders}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e002](#e002): Bad XML

Failed to parse XML: '{xml}'



![color e image](../color-error.png)

### [e003](#e003): Invalid node name

Invalid node name '{node_name}' in flow XML '{flow_path}'. Node names must be alphanumeric with dot, dash, or underscores. Must match the regex: {regex}


[More info](https://regex101.com/)



![color e image](../color-error.png)

### [e004](#e004): Broken symlink

The target of soft link '{link}' does not exist.


[More info](https://www.google.com/search?q=linux+find+broken+symlinks)



![color e image](../color-error.png)

### [e005](#e005): Scattered module flow

The flow XML children for module '{module_name}' are defined in more than one flow XML:\n{flow_xmls}


[More info](https://gitlab.science.gc.ca/CMOI/mflow-prototype/issues/23#note_189290)



![color e image](../color-error.png)

### [e007](#e007): Missing required resource file

The task '{task_path}' has no resource file at '{resource_path}'. This is required for the '{context}' context.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e008](#e008): Missing curly brackets in resource xml

Variables in resource XMLs must use curly brackets like '${{ABC}}' not '$ABC'. The file '{file_path}' contains:\n{matching_string}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e009](#e009): Unbalanced curly brackets in resource xml

Found an uneven number of curly brackets '{attribute_value}' in a resource file: '{file_path}'



![color e image](../color-error.png)

### [e010](#e010): Hard coded path in config file

The path '{bad_path}' defined in '{config_path}' is absolute and does not start with a variable like '${{SEQ_EXP_HOME}}'. This is a less portable and more fragile way to configure an experiment.



![color e image](../color-error.png)

### [e011](#e011): Bad dependency experiment

The 'exp' attribute '{exp_value}' in the resources file '{resource_path}' is not a path to a folder that exists.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e012](#e012): Undefined resource XML variables

The resource XML '{resource_path}' uses variables that are not defined in any resource files like 'resources/resources.def'. Variables:\n{variable_names}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e013](#e013): Dissemination state does not match context

The experiment seems to have the '{context}' context but variables in '{cfg_path}' do not match what is expected: {unexpected}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Dissemination)



![color e image](../color-error.png)

### [e014](#e014): Non-links in hub

Experiments with the '{context}' context can only have soft link folders in their 'hub' folder:\n{bad}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/hub)



![color e image](../color-error.png)

### [e015](#e015): Resource value higher than maximum

The resource value '{value}' for '{attribute}' in '{xml_path}' is higher than the maximum of '{maximum}' defined in jobctl-qstat for queue '{queue}'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e016](#e016): No git repo

There is no git repo tracking this experiment. Experiments with the '{context}' context should always be version controlled with git.



![color e image](../color-error.png)

### [e017](#e017): Duplicate name in flow container

The container '{container_name}' in a flow XML has more than one element with the name or subname '{duplicate_name}'. All direct children in a container must have a unique name or subname.



![color e image](../color-error.png)

### [e018](#e018): Submits element has name attribute

All SUBMITS elements should have a 'sub_name' attribute not a 'name' attribute. The file '{file_path}' contains:\n{matching_string}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color e image](../color-error.png)

### [e019](#e019): Non-submits element has sub_name attribute

Only SUBMITS elements should have a 'sub_name' attribute. You may need to use the 'name' attribute instead. The file '{file_path}' contains:\n{matching_string}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color e image](../color-error.png)

### [e020](#e020): Inconsistent log folder owners or permissions

The log folder '{path}' has ownership and permissions '{ugp}' which is different from the other log folders. The permissions of the temporary log folders should be the same: {folders}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e021](#e021): Duplicate resource definitions

The variable '{variable}' is defined more than once in the file '{path}'. Tools like getdef may behave unexpectedly.



![color e image](../color-error.png)

### [e022](#e022): Missing stats folder

The 'stats' folder is missing but required because the resource variables SEQ_RUN_STATS_ON and SEQ_AVERAGE_WINDOW are used: '{required}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/stats)



![color e image](../color-error.png)

### [e023](#e023): Bad loop expression

The file '{path}' has a bad loop expression '{loop_expression}'. This should be comma delimited sets of numbers in the format 'start:end:step:set'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/1.5.0/Release_Notes#Multi-definition_numeric_loops)



![color e image](../color-error.png)

### [e024](#e024): Bad permissions on operational log folders

The log folder '{folder}' should have '{expected}' permissions but instead it has '{ugp}'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e025](#e025): Realpath link is non-operational path

The experiment seems to have the '{context}' context but the file '{path}' contains references to a non-operational user's home:\n{bad}



![color e image](../color-error.png)

### [e026](#e026): Link chain contains non-operational path

The experiment seems to have the '{context}' context but the file '{path}' is a chain of links, which contains a non-operational user's home. The realpath for the link is okay, but traversing it is not:\n{bad}



![color e image](../color-error.png)

### [e027](#e027): Bad shell script syntax

The command '{verify_cmd}' found errors in the shell script '{path}'. Output:\n{output}



![color e image](../color-error.png)

### [e028](#e028): External dependency is relative

The file '{resource_path}' has a relative 'dep_name' attribute '{dep_name}' but the 'exp' is external. External dependencies cannot be relative.



![color e image](../color-error.png)

# Level: Warning
![color w image](../color-warning.png)

### [w001](#w001): Missing resource file

The task '{task_path}' has no resource file at '{resource_path}'. Create a resource file to avoid using unknown defaults.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color w image](../color-warning.png)

### [w002](#w002): Missing loop resource file

The loop or switch '{node_path}' has no resource file at '{resource_path}'. Create a resource file to avoid using unknown defaults.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color w image](../color-warning.png)

### [w003](#w003): Deprecated site1/site2

The paths site1 and site2 are no longer available after the upgrades in early 2020. The file '{file_path}' contains:\n{matching_string}



![color w image](../color-warning.png)

### [w004](#w004): Deprecated hall1/hall2

The paths hall1 and hall2 are no longer available after the upgrades in early 2020. The file '{file_path}' contains:\n{matching_string}



![color w image](../color-warning.png)

### [w005](#w005): Multiple homes for project

The maestro experiment is found in the home folder '{real_home}' but core maestro files are soft links to other user homes. This may be considered too unstable to install operationally. Run realpath on these links:\n{bad_links}


[More info](https://wiki.cmc.ec.gc.ca/wiki/User:Maciaa/home_references)



![color w image](../color-warning.png)

### [w006](#w006): Hard coded path in config file

The path '{bad_path}' defined in '{config_path}' is absolute and does not start with a variable like '${{SEQ_EXP_HOME}}'. This is a less portable and more fragile way to configure an experiment.


[More info](https://wiki.cmc.ec.gc.ca/wiki/SEQ_EXP_HOME)



![color w image](../color-warning.png)

### [w007](#w007): No support status in operational experiment

There is no SupportInfo attribute in the XML '{xml_path}' or the XML does not exist. This is required for operational experiments.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color w image](../color-warning.png)

### [w008](#w008): Multiple support statuses

The XML '{xml_path}' has more than one SupportInfo element.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color w image](../color-warning.png)

### [w009](#w009): Resource variable typo

The resource variable '{maybe_typo}' is defined but the standard variable name '{expected}' is not. Did you mean that instead?


[More info](https://wiki.cmc.ec.gc.ca/wiki/User:Lims/projects/tech_transfer_improvements#Using_standard_variables_for_machine_and_queue_definitions)



![color w image](../color-warning.png)

### [w010](#w010): Bad queue value for resource variable

The value '{value}' for the resource variable '{name}' is not a queue available in qstat. Queues:\n{queues}



![color w image](../color-warning.png)

### [w011](#w011): Experiment not in overview XML

The experiment seems to have the '{context}' context but it was not found in the {exp_count} experiments in the overview XML: {xml_path}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/overview_xml)



![color w image](../color-warning.png)

### [w012](#w012): Experiment in unexpected overview XML

The experiment seems to have the '{context}' context but it was found in the {exp_count} experiments in the '{xml_context}' context overview XML: {xml_path}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/overview_xml)



![color w image](../color-warning.png)

### [w013](#w013): Misplaced dissemination variables

The variables {variables} belong only in 'experiment.cfg' files but were found in: '{cfg_path}'


[More info](https://wiki.cmc.ec.gc.ca/wiki/Dissemination)



![color w image](../color-warning.png)

### [w014](#w014): Hub pairs have dissimilar targets

The hub folder links '{folder1}' and '{folder2}' are expected to have similar targets. Instead they are very different:\n{target1}\n{target2}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/hub)



![color w image](../color-warning.png)

### [w015](#w015): Git repo has uncommited changes

There are uncommited changes in the git repo. Experiments with the '{context}' context should always have nothing to commit and a clean working tree from 'git status'.



![color w image](../color-warning.png)

### [w016](#w016): The task run_orji is disabled

The task resource '{resource_path}' has a catchup value of '{catchup}' but 'run_orji' tasks should always be enabled. This way, users get to decide whether to subscribe or unsubscribe.


[More info](https://wiki.cmc.ec.gc.ca/wiki/orji)



![color w image](../color-warning.png)

### [w017](#w017): Archive file is not a link

The archive file '{bad}' is not a link. Files named '.protocole_*' or '.archive_monitor_*' must be links so that the maintainers of the archive system can more easily manage its settings.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Archive)



![color w image](../color-warning.png)

### [w018](#w018): Bad items in gitignore

The gitignore file '{gitignore_path}' should not contain line '{line}'. It's important that this pattern is in the git repository so a full working suite can be shared.



![color w image](../color-warning.png)

### [w019](#w019): Missing items in gitignore

The gitignore file '{gitignore_path}' should contain {content}. This will ignore files generated when running this suite which do not belong in the version controlled project.



![color w image](../color-warning.png)

### [w020](#w020): No gitignore

There should be a gitignore file here: '{gitignore_path}'. No gitignore means large amounts of unimportant files may be accidentally shared or added to the project.



![color w image](../color-warning.png)

### [w021](#w021): Maestro file in $CMCCONST

The realpath for file '{path}' is in the $CMCCONST folder '{cmcconst}'. Task, config, flow, and resource XML files used in a suite should not be in the $CMCCONST folder.


[More info](https://gitlab.science.gc.ca/CMOI/best-practices/blob/master/en/constants.md)



![color w image](../color-warning.png)

### [w022](#w022): Machine resource is hard coded

The experiment seems to have the '{context}' context but the value '{machine_value}' of 'machine' in '{resource_path}' is hard coded. A switchover may break this suite. Use a variable like $FRONTEND instead.



![color w image](../color-warning.png)

### [w023](#w023): Operational user can overwrite experiment

The operational user '{user}' has write permissions on the permanent project file '{path}'. For safety during operational runs, '{user}' should only have read and execution permissions for permanent project files.


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w024](#w024): Parallel user in operational context

The experiment seems to have the '{context}' context but the file '{file_path}' references the parallel systems with the string '{par_string}'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w025](#w025): Operational files have incorrect owner

The experiment seems to have the '{context}' context but the file '{path}' is owned by '{owner}' whereas '{expected}' is expected.


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w026](#w026): Wallclock much bigger than history requires

The wallclock for '{node_path}' is set to '{wallclock_seconds}' seconds in '{resource_xml}' but the latest successful run on '{datestamp}' only took '{latest_seconds}' seconds. This is {factor} times bigger (the threshold for this message is {threshold}). The wallclock should probably be lowered.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Wallclock)



![color w image](../color-warning.png)

### [w027](#w027): Clobbered SSM packages

Different versions of the SSM package '{package}' are used: {versions}. The same version should be used by all, or the package should only be added to the environment in one root place. Files:\n{paths}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Ssm)



![color w image](../color-warning.png)

### [w028](#w028): Suite path in resources without datestamp

The resource file '{resource_path}' has generic references to maestro project paths which don't use datestamps like '_20200401'. This may cause issues with troubleshooting, history, and transfers. Paths:\n{bad}


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w029](#w029): No soft link on operational home

The experiment path '{target}' is where operational suites are installed, however there is no soft link '{source}' pointing to it.


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w030](#w030): Deprecated uspmadt system

The '-r' or '-t' options used in '{path}' with 'fname', 'fgen+', or 'dtstmp' should not be a 'run' variable. This uses the deprecated uspmadt system. Use 'CMCSTAMP' instead. Lines:\n{lines}


[More info](https://gitlab.science.gc.ca/CMOI-Service-Desk/General/issues/5)



![color w image](../color-warning.png)

### [w031](#w031): Missing required variables in resources.def

The file '{path}' must define the variables {required} however these were missing: {missing}


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMDI/Good_practices)



![color w image](../color-warning.png)

### [w032](#w032): Bad dependency node path

The file '{resource_path}' describes a node path '{node_path}' which does not exist. Maestro might ignore this dependency.



![color w image](../color-warning.png)

### [w033](#w033): Bad relative dependency node path

The file '{resource_path}' has a 'dep_name' attribute '{dep_name}' which describes a node path '{node_path}' which does not exist relative to '{node_folder}'. Maestro might ignore this dependency.



![color w image](../color-warning.png)

### [w034](#w034): Bad external dependency node path

The file '{resource_path}' describes a node path '{node_path}' which does not exist in experiment '{exp}'. Maestro might ignore this dependency.



![color w image](../color-warning.png)

### [w035](#w035): Bad external dependency experiment

The file '{resource_path}' describes an experiment '{exp}' which does not exist, or is broken. Maestro might ignore this dependency.



![color w image](../color-warning.png)

### [w036](#w036): No archiving in hub

The 'hub' folder seems to have subfolders containing more than {file_count} files from more than {day_count} days but no '.protocole_*' archiving file. These files may accumulate:\n{folders}



![color w image](../color-warning.png)

# Level: Info
![color i image](../color-info.png)

### [i001](#i001): Multiple homes for project

The maestro experiment is found in the home folder '{real_home}' but core maestro files are soft links to other user homes. This may be unstable. Links:\n{bad_links}


[More info](https://wiki.cmc.ec.gc.ca/wiki/User:Maciaa/home_references)



![color i image](../color-info.png)

### [i002](#i002): Module name and path differ

The module folder '{folder_name}' differs from the module name '{attribute_name}' in the flow XML '{xml_path}'. This can help organize a project, but it may also be confusing.



![color i image](../color-info.png)

### [i003](#i003): Text editor swap files

Text editor swap files were found, for example for vim or emacs. If your editor is closed, you may want to recover or delete these:\n{swaps}


[More info](https://www.google.com/search?q=what+is+a+text+editor+swap+file)



![color i image](../color-info.png)

### [i004](#i004): Git repo has uncommited changes

There are uncommited changes in the git repo.



![color i image](../color-info.png)

### [i005](#i005): Unknown nodelogger signal

The executable 'nodelogger' was given a signal for its '-s' argument that is not a known signal: {signals}. This message won't appear in the message center. If you don't want it to appear in the message center, use 'infox'. \n{details}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Nodelogger)



![color i image](../color-info.png)

### [i006](#i006): Lead developers from git history

Based on the git history for this project (commit frequency, recency, continuity) these seem to be the lead developers:\n{developers}



![color i image](../color-info.png)

### [i007](#i007): Absolute developer paths

The file '{path}' contains absolute paths to a non-operational user's home. This cannot be installed operationally:\n{bad}



![color i image](../color-info.png)

### [i008](#i008): Old SSM version

The file '{path}' uses an SSM package '{old}' but a newer version '{new}' is available.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Ssm)



![color i image](../color-info.png)

### [i009](#i009): Resources with valid hours

Tasks in this project have resource configurations which change depending on time of day. Look for the 'valid_hour' or 'valid_dow' attributes:\n{paths}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color i image](../color-info.png)

### [i010](#i010): No hcrons

No active configuration files for '{suite_name}' were found in '{hcron_folder}'. The suite may not run automatically.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Hcron)



![color i image](../color-info.png)

# Level: Best practice
![color b image](../color-best-practice.png)

### [b001](#b001): Hard coded dependency path

The 'exp' attribute '{exp_value}' in the resources file '{resource_path}' is hard coded. This is less portable and more fragile. Consider using a variable instead.



![color b image](../color-best-practice.png)

### [b002](#b002): SupportInfo is too long

The SupportInfo attribute in the XML '{xml_path}' is '{char_count}' characters long but it should be shorter. The recommended maximum is {max_chars} characters.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b003](#b003): SupportInfo has no URL

The SupportInfo attribute in the XML '{xml_path}' should contain a URL. This is the recommended way to provide detailed support status info and troubleshooting steps.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b004](#b004): Non-standard SupportInfo text

The SupportInfo attribute in the XML '{xml_path}' should start with a value like 'Full Support'. Recommended start strings:\n{substrings}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b005](#b005): Deprecated file or folder

The use of file or folder '{path}' is deprecated and should be deleted.



![color b image](../color-best-practice.png)

### [b006](#b006): Non-maestro files in maestro folders

The maestro folder '{folder}' should only contain maestro files like tsk, cfg, xml. These files were found:\n{filenames}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color b image](../color-best-practice.png)

### [b007](#b007): Comments in config file

The pseudo-xml section (containing input, executables, and output) of the config file '{file_path}' contains {count} commented lines starting with "##". These seem to be configuration lines and not comments, and should be removed.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/.cfg)



![color b image](../color-best-practice.png)

### [b008](#b008): Hidden queue alias used

The value '{value}' for the resource variable '{name}' is a hidden queue alias not easily visible in qstat. Consider using one of these queues instead:\n{queues}



![color b image](../color-best-practice.png)

### [b009](#b009): Deprecated attribute in SUBMITS element

The file '{xml_path}' has the attribute 'type' in a SUBMITS element. This is deprecated and can be removed.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color b image](../color-best-practice.png)

### [b010](#b010): Non-standard characters in executable name

The config path '{bad}' in '{config_path}' has non-standard characters that do not match regex '{regex}'. This can cause bugs with tools, operating systems, and parsers. Consider renaming them. {dollar_msg}


[More info](https://regex101.com/)



![color b image](../color-best-practice.png)

### [b011](#b011): Top-level file or folder in CMCCONST

There are references to files or folders in the root level of the CMCCONST folder. It is recommended instead to use folders in CMCCONST. The file '{file_path}' contains:\n{matching_string}


[More info](https://gitlab.science.gc.ca/CMOI/best-practices/blob/master/en/constants.md)



![color b image](../color-best-practice.png)

### [b012](#b012): Deprecated archive file

The file '{bad}' is a deprecated archive file and should be deleted. If the hub has no other archive files, its archiving status should be examined.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Archive)



![color b image](../color-best-practice.png)

### [b013](#b013): Unclear folder name

The folder '{unclear}' should have a descriptive soft link next to it. For example 'forecast -> e1'. This gives newbies one less thing to memorize when getting started.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Obfuscation)



![color b image](../color-best-practice.png)

### [b014](#b014): Bad node name

Bad node name '{node_name}' in flow XML '{flow_path}'. This name works, but the recommendation is to match this regex: {regex}


[More info](https://regex101.com/)



![color b image](../color-best-practice.png)

### [b015](#b015): Non-standard variables in batch resource

The BATCH attribute '{attribute_name}' in '{resource_path}' uses a non-standard variable '{attribute_value}'. Consider using a standard variable instead so configuration is easier to track and change: {recommended}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color b image](../color-best-practice.png)

### [b016](#b016): Inconsistent file owners or permissions

The file '{path}' has ownership and permissions '{ugp}' but most experiment files have '{expected}'. The owner, group, and permissions of permanent experiment files should be the same.



![color b image](../color-best-practice.png)

### [b017](#b017): Found SEQ_ instead of MAESTRO_

The deprecated variable '{old}' was found in '{path}'. Consider using the equivalent variable '{new}' available in maestro 1.8+ instead. This helps newbies understand your project since they will know this variable is related to maestro.



![color b image](../color-best-practice.png)

### [b018](#b018): Uppercase variable is redefined

The uppercase variable '{variable}' is defined more than once in the file '{path}'. Uppercase variables in bash should be considered constant and not changed. Note that "const" in other programming languages can only be defined once.


[More info](https://google.github.io/styleguide/shellguide.html#s7.3-constants-and-environment-variable-names)



![color b image](../color-best-practice.png)

### [b019](#b019): Readme is not markdown

The file '{readme}' looks like a 'read me' file. Consider writing it in markdown and renaming it to '{suggested}' so that it appears automatically and formatted on platforms like GitLab.


[More info](https://www.youtube.com/watch?v=SCAfcuQ0dBE)



![color b image](../color-best-practice.png)

### [b020](#b020): Literal path instead of CMCPROD

Literal paths to 'hall3' or 'hall4' were found. Consider using the CMCPROD variable instead so your project follows switchover configurations. The file '{file_path}' contains:\n{matching_string}


[More info](https://wiki.cmc.ec.gc.ca/wiki/Cmcprod)



![color b image](../color-best-practice.png)

### [b021](#b021): Absolute path in config instead of getdef

The configuration file '{config}' should use getdef instead of absolute hard coded paths. For example: ABC=$(getdef resources ABC)\nAbsolute paths:\n{values}


[More info](https://wiki.cmc.ec.gc.ca/wiki/User:Lims/projects/tech_transfer_improvements#Making_variables_configurable_from_high_level)



![color b image](../color-best-practice.png)

### [b022](#b022): Identical files in module

The content of files in the same module are identical. Consider replacing duplicate files with soft links to one file, so fixing and updating one fixes and updates all. Or distinguish the files with comments. Files:\n{paths}


[More info](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)



![color b image](../color-best-practice.png)

### [b023](#b023): Etiket variables not defined in etikets.cfg

The etiket variables {etikets} were defined in '{bad_path}' but they should be defined in '{good_path}'. Etiket variables are discovered by this scanner based on their "ETIK" name and the use of 'pgsm' and 'editfst'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/Etikets.cfg)



![color b image](../color-best-practice.png)

### [b024](#b024): Defined but unused configuration variables

The configuration file '{config}' defines the variables '{unused}' but they are not used. Consider removing them.



![color b image](../color-best-practice.png)

### [b025](#b025): Bad git remote origin

The experiment seems to have the '{context}' context but the git remote 'origin' points to '{bad}'. Instead the remote should start with '{good}'.



![color b image](../color-best-practice.png)

### [b026](#b026): Shell script syntax recommendations

The command '{verify_cmd}' recommends changes to the shell script '{path}'. Output:\n{output}



![color b image](../color-best-practice.png)

### [b027](#b027): Non-standard maestro command path

The command '{cmd}' in '{path}' for the maestro tool '{tool}' should be preceded by '{prefix1}' or '{prefix2}' like '{expected}'.



![color b image](../color-best-practice.png)

### [b028](#b028): Bad EntryModule target

The target for the link '{path}' should be '{good}' instead of '{bad}'.


[More info](https://wiki.cmc.ec.gc.ca/wiki/CMDI/Good_practices)



![color b image](../color-best-practice.png)

### [b029](#b029): Deprecated products_dbase link

The folder '{bad}' in 'hub' should not be a link. This style of product database is deprecated.


[More info](https://gitlab.science.gc.ca/CMOI/maestro/issues/219)



![color b image](../color-best-practice.png)

### [b030](#b030): Bad SSM domain variable name

The file '{path}' uses variables as SSM domains, but the names do not start with 'SSM_':\n{variables}



![color b image](../color-best-practice.png)

### [b031](#b031): Compiled executable in project

The file '{path}' seems to be a compiled executable. These belong outside the maestro project, or perhaps in an SSM package.



![color b image](../color-best-practice.png)

### [b032](#b032): Unused file in bin folder

The file '{path}' in the 'bin' folder is not used in any 'cfg' or 'tsk' file. Consider deleting it from the project.


![color b image](../color-best-practice.png)

# Generated Page

This page was generated by the 'generate_messages_markdown.py' script from the repo 'https://gitlab.science.gc.ca/CMOI/maestro' on '2020-10-08'.
