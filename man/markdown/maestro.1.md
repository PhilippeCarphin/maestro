maestro -- API for the main engine in the Maestro sequencer package
=============================================

## SYNOPSIS

`maestro -n node -s signal -e exp [-i] [-v] [-d <YYYYMMDDhhmmss>] [-l <loopargs>] [-f <flow-value>] [-o <extra_soumet_args>]`

## DESCRIPTION

`maestro` is a core utility in the Maestro project. It sends `submit`, `begin`, `end`, `abort`, `initbranch`, or `initnode` signals to a Maestro experiment and its tasks. This utility is most often used by `xflow` invisibly in its backend. However you can also send these signals using this commandline utility.

When signals are sent to tasks several things happen. `maestro` verifies dependencies, it may trigger other tasks, it creates processes, it may call itself recursively, and it writes several types of logs. This utility manages that complexity.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-s, --signal <signal>:` Required argument. The `-s submit` signal submits a node execution request. You can `-s begin`, `-s end`, or `-s abort` node execution. `-s initbranch` sends a branch initialization, which is only effective for container nodes. This will clear the status for the current container node and any children nodes. `-s initnode` initializes a node, but it's only effective on leaf nodes.
* `-n, --node <node-path>:` Required argument. Specify the full path of task or family node. This is mandatory unless `-f root` is used, which specifies the first node at the root of the experiment.
* `-d <YYYYMMDDhhmmss>:` Launch a cron to submit on this 14 character date. Example: `20080530000000`. Anything shorter will be padded with zeroes. The default value is the date of the experiment. A date earlier than now will submit immediately. The order of precedence for dates are the `-d` argument, followed by the `SEQ_DATE` environment variable, and finally the latest modified log file under the directory `$SEQ_EXP_HOME/logs`. If none of those exist, the command will assume the epoch date, that is `197001010000`. 
* `-f, --flow <flow-value>:` Supported values are `continue` or `stop`. Default value is continue. For a task node, this option tells the sequencer whether to continue or stop flow execution after the current node has completed. For a container node, this option specifies whether or not its children will be submitted for execution when the container is in its begin state.
* `-i:` Ignore dependencies and catchup values. Submit the current node for execution despite any unsatified dependencies or catchup values.
* `-o, --extra-soumet-args:` Additional arguments being given to ord_soumet by the job besides the usual ones used by the sequencer. This argument has precedence over any argument defined in the job's resources file in case of multiple definitions. Example: `-o -waste=50`.
* `-l, --loop-args <loop-arguments>:` Specify the loop arguments as a comma seperated value loop index. Example: `-l inner_Loop=1,outer_Loop=3`. Loop nodes without `-l` will submit the whole loop. If `-l` is given for a switch, the submits of the switch will be based on that value. Otherwise, the datestamp will be used. 
* `-v:` Verbose tracing output. One may set this also by setting the `SEQ_TRACE_LEVEL` environment variable to `TL_FULL_TRACE`, `TL_MEDIUM`, `TL_ERROR` or `TL_CRITICAL`.

## EXAMPLES

Submit node and continue flow on completion:

```
maestro -s submit -n /enkf_mod/anal_mod/Analysis/enkf_pre
```

Submit node, ignore dependencies and do not submit next tasks on completion:

```
maestro -s submit -n /enkf_mod/anal_mod/Analysis/enkf_pre -i -f stop
```

Submit gem_mod loop member iteration 18:

```
maestro -s submit -n /enkf_mod/Trials/gem_loop/gem_mod -l gem_loop=18
```

Submit npass_task Sortie loop member iteration 18, iteration number 0000000018

```
maestro -s submit -n /enkf_mod/Trials/gem_loop/gem_mod/Sortie -l gem_loop=18,Sortie=0000000018
```

Submit run_mod using extra arguments to allow a cpu waste of 10%:

```
maestro -s submit -n /enkf_mod/Forecasts/gem_loop/gem_mod/Runmod -l gem_loop=18 -o "-waste 10"
```
