task_setup.py -- create a sandbox for a task to run in
=============================================

## SYNOPSIS

`task_setup.py [-vcfd] [-b <base-directory>] [-e=<file>] [--varcache=<file>] <configuration-file>`

## DESCRIPTION

`task_setup.py` is not often called directly. See `task_setup.dot` for the more commonly used task setup command.

`task_setup.py` creates a sandbox for a task (script) to run in. This may involve creating the folders `.setup`, `bin`, `input`, `output`, and `work` and populating them with configuration files passed to the utility. This "sandbox" for a given task contains links to all of the inputs, executables, outputs, and temporary scratch space required by a task. This task directory layout is important for auditability, since it is clear from the contents of the sandbox exactly what data and executables were used during the execution of the task itself.

`<configuration-file>` is the path to the configuration file to be read. A task setup configuration file is divided into two sections: variable declarations and task setup instructions. Variable declarations are made as standard shell variable declarations. The task setup instructions appear as a comment block but are interpreted by task setup to construct the task directory layout. Here's an example task setup configuration file:

```
# Variable Declaration Section
DATA_DIR=/path/to/some/analysis/file/location                           # 1
RUN_NAME=G100                                                           # 2
MORE_DATA=${EXTRAS:-'<no value>'}                                       # 3
# Task Setup Instruction Section
#############################################
# <input>                                                               # 4
# analysis     ${DATA_DIR}/`dtstmp ${RUN_NAME} -Y -m -d -H`_000         # 5
# analysis_ext ${MORE_DATA}                                             # 6
# </input>                                                              # 7
# <executables>                                                         # 8
# pgsm         pgsm6.19.7                                               # 9
# </executables>                                                        # 10
# <output>                                                              # 11
# interp_out   ${DATA_DIR}/interpolated_output.fst                      # 12
# </output>                                                             # 13
#############################################
```

For more information about configuration files for task setup, see: https://wiki.cmc.ec.gc.ca/wiki/Task_setup/userguide#Configuration_Files

For more information about task setup, see: https://wiki.cmc.ec.gc.ca/wiki/Task_setup

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-b <base-directory>, --base=<base-directory>:` path of the working directory to be used as the base for task subdirectory setup. If no `-b` is provided, use the present working directory. This should point to a location where you have sufficient disk space to handle the temporary files generated during the task's execution.
* `-d, --dry-run:` Do not perform directory creation and linking operations, just process the configuration file.
* `-c, --clean:` If the utility finds any pre-existing sandbox folders in `<base-directory>`, remove them.
* `-r, --force:` If `-c` is used but `<base-directory>` does not match a sandbox structure, the script aborts. This prevents accidental deletion of other files. Use this option to force cleaning.
* `-v, --verbose:` Verbose runtime output.
* `-e <file>, --environment=<file>:` Used by `task_setup.dot` and unlikely to be useful to users. An `<environment-file>` contains a bunch of `variable=value` statements which are used by the task setup utility.
* `--varcache=<file>:` Path to a text file containing a bash namespace cache of variables. This option is used internally by `task_setup.dot` to avoid polluting the namespace while tasks are executed. It does this by writing variable cache files to a temporary file.

## EXAMPLES

Create the `.setup`, `bin`, `input`, `output`, and `work` folders in `~/tmp` for the "mod_direct_1000" node in the RDPS, r1 suite. Note that `bin` is populated with shortcuts to the bins for this task, and `.setup` is populated with `task_setup*` files, etc:

```
cd ~/tmp
task_setup.py /home/smco500/.suites/rdps/r1/modules/cmdm_post_processing/mod_direct/mod_direct_loop/mod_direct_1000.cfg
```
