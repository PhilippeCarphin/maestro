nodeinfo -- send signals to Maestro nodes
=============================================

## SYNOPSIS

`nodeinfo -n node [-e exp] [-l <loopargs>] [-f <filter-whitelist>]`

## DESCRIPTION

`maestro` is a core utility in the Maestro project. It sends `submit`, `begin`, `end`, `abort`, `initbranch`, or `initnode` signals to a Maestro experiment and its tasks. This utility is most often used by `xflow` invisibly in its backend. However you can also send these signals using this commandline utility.

When signals are sent to tasks several things happen. `maestro` verifies dependencies, it may trigger other tasks, it creates processes, it may call itself recursively, and it writes several types of logs. This utility manages that complexity.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-n, --node <node-path>:` Required argument. Specify the full path of task or family node. This is mandatory unless `-f root` is used, which specifies the first node at the root of the experiment.
* `-e <path-to-exp-folder>`: By default nodeinfo will search the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-f, --filters <filter-whitelist>`: Use search filters, for example `-f cfg,res`. If this option is used, only search those file types. Available filters are: `all` by default, but does not include var, `task` for node task path, `cfg` for node config path, `res` for resource definitions, `res_path` for node resource path, `type` to show node type like "Task", `node` for node name and loop extension if applicable, `root` for the path of the root node, `var` for all environment variable exports, and finally `dep` to see node dependencies.
* `-l, --loop-args <loop-arguments>:` Specify the loop arguments as a comma seperated value loop index. Example: `-l run=18`.
* `-v:` Verbose tracing output.

## EXAMPLES

A great way to see examples of nodeinfo is to launch `xflow`, right click on a node, click info, and click node info. The top line will be a nodeinfo example. Here are some more examples:

Get nodeinfo for "run_loop_on_hours_54" in the RDPS, r1 experiment for run 18:

```
nodeinfo -n /main/cmdw_post_processing/blending/run/loop_on_hours_54 -e /home/smco500/.suites/rdps/r1 -l run=18 
```

Get nodeinfo for configuration and resources from an experiment in the present working directory:

```
nodeinfo -e `pwd` -n /main/post_proc/loop_b -f cfg,res
```

Get node dependencies for the run_orji task in the GDWPS forecast run:

```
nodeinfo -e /home/smco500/.suites/gdwps/forecast -n gdwps/run_orji -f dep
```
