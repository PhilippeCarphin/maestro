nodelogger -- send a message to the log server and message center
=============================================

## SYNOPSIS

`nodelogger -n <node> -s <signal> -m <message> [-e <path-to-experiment>] [-l <loop-args>] [-d <YYYYMMDDhhmmss>]`

## DESCRIPTION

`nodelogger` is used by nodes to communicate messages to the Maestro log server and xflow message center. Every message requires a node, signal type, and message. Often nodelogger is written inside `tsk` files in maestro projects. These messages can update the state of a node - for example a nodelogger with the `abort` message will update the node to be in the abort state.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-n, --node <node-path>:` Required. Specify the full path of task or family node.
* `-s, --signal <signal>:` Required. This can be any string, however some strings have special meaning: `info` adds the message to the task log and message center. `infox` adds the message to the task log. `init`, `submit`, `begin`, `end`, and `abort` sets the node to that state.
* `-m <message>:` Required. Message should be enclosed in double quotes.
* `-d <YYYYMMDDhhmmss>:` Allows the log message to be sent to an experiment datefile different from the default one. If the datestamp file does not exist, it will be created. Example: `20080530000000`. Anything shorter will be padded with zeroes.
* `-e <path-to-exp-folder>`: By default nodelogger will search the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-l, --loop-args <loop-arguments>:` Specify the loop arguments as a comma seperated value loop index. Example: `-l run=18`.
* `-v`: Enable verbose debug output.

## EXAMPLES

A great way to see examples of nodelogger is to search an existing experiment for nodelogger:

```
grep -rn "nodelogger" ~smco500/.suites/rdps/r1/modules/
```

Often lines inside `tsk` files will include special environment variables like `SEQ_NODE`. This example from within a `tsk` file will log a "info" message showing the value of that variable:

```
nodelogger -n ${SEQ_NODE} ${SEQ_LOOP_ARGS} -s info -m "a message from ${SEQ_NODE}! the value for SUPER_DUPER is '${SUPER_DUPER}'"
```
