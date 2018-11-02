chaindot.py -- construct one configuration file out of many for one node
=============================================

## SYNOPSIS

`chaindot.py -n <node> -o <output-file> [-e <path-to-experiment-folder>]`

## DESCRIPTION

`chaindot.py` builds a single configuration file out of many for one node. The file created by this tool can be passed to `task_setup.dot` as a complete configuration file to setup the task's environment and temporary work directories. This tool is mostly used internally by Maestro for this purpose.

For more information on Maestro, see https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-n <node-path>:` Required. Specify the full path of a task or family node.
* `-e <path-to-exp-folder>`: By default chaindot.py will search the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-o <output-file>:` Required. This output file contains all in-scope variables for the given node. This file is a dottable file, meaning you can do this in bash: `. ./my_chaindot_file` to set up an environment corresponding to your `-n` node.

## EXAMPLES

To see a working example of `chaindot.py`, open up an experiment with `xflow`, right click a task, click info, and click `node batch`. You can search the node batch file which was opened for `chaindot.py`.

The following example will navigate to the experiment RDWPS. Then, combine the configuration files which apply to the node `wave_nml_output`.  Finally it writes the output to a file `chaindot-test.cfg`:

```
cd /home/smco500/.suites/rdwps
chaindot.py -e `pwd` -n rdwps/hum/preproc/Namelists/wave_nml_output -o ~/tmp/chaindot-test.cfg
```

This example is the same as above, except instead of creating a file it writes to `/dev/stdout` which means it will print to standard output, or print to your console:

```
cd /home/smco500/.suites/rdwps
chaindot.py -e `pwd` -n rdwps/hum/preproc/Namelists/wave_nml_output -o /dev/stdout
```
