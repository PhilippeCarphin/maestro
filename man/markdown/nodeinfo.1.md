nodeinfo -- send signals to Maestro nodes
=============================================

## SYNOPSIS

`nodeinfo -n <node> [-e <path-to-experiment-folder>] [-l <loopargs>] [-f <filter-whitelist>]`

## DESCRIPTION

`nodeinfo` prints human readable information about a Maestro node. This information includes its name, type (example: Loop), catchup value, machine (example: eccc-ppp1), configuration path, resources path, and many other values. This is the output produced in `xflow` with the `node info` menu option.

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
