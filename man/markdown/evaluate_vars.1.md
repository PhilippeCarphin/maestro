evaluate_vars -- examine the environment variables set in Maestro tasks
=============================================

## SYNOPSIS

`evaluate_vars -n <node> [-fv] [-l <loop-args>] [-m <machine>] [-o <output-path>]`

## DESCRIPTION

`evaluate_vars` shows the value of environment variables when a maestro task is run. It does this by connecting to a remote machine by SSH so that a profile is set up as it would be in a maestro run, and then by executing the the configuration file for a given node. Use the `-f` option to execute the full hierarchy of configuration files for that node. `SEQ_EXP_HOME` is always used to find the experiment.

An environment's configuration when nodes are run may depend on the machine, architecture, user, profile settings, and maestro configuration files that apply to a node. For example there may be cases within a startup profile where an environment variable is set differently depending on machine architecture. This utility handles this complexity for you to show environment variables.

For more information on profiles and environment configuration, see: https://wiki.cmc.ec.gc.ca/wiki/HPCS/ordenv

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-n, --node <node-path>:` Required. Specify the full path of task or family node.
* `-l, --loop-args <loop-arguments>:` Specify the loop arguments as a comma seperated value loop index. Example: `-l run=18`.
* `-m <machine>:` By default, evaluate_vars will use the value of `node.machine` given by `nodeinfo` using the `-n` argument provided to this script. Use this option to choose some other machine, for example: `-m eccc-ppp1`.
* `-o <output-path>:` By default, evaluate_vars will print to console lots of output. This includes output from setting up your remote profile like "=== ordenv: completed ===" as well as the evaluate_vars output. If you provide an output path like `-o ~/tmp/evaluate_vars.log` then it will write just the evaluate_vars output (no profile setup) to that path.
* `-f:` By default, configuration will use the value of `node.configpath` given by `nodeinfo` using the `-n` and `-l` arguments provided to this script. Use this option to use the full configuration discovered with the `chaindot.py` utility.
* `-v`: Enable verbose debug output.

## EXAMPLES

A great way to see examples of evaluate_vars is to open `xflow`, right click on a node, click "info", and click "evaluated node config". Here's another example:

This will show the full (`-f`) environment variables for the prog node in the REWPS experiment using the machine `eccc-ppp1` and write output to `~/tmp/evaluate_vars.log`.

```
cd /home/smco500/.suites/rewps/forecast
export SEQ_EXP_HOME=`pwd`
evaluate_vars -n /rewps/prog -m eccc-ppp1 -f -o ~/tmp/evaluate_vars.log
```
