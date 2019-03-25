getdef -- search a file and overrides.def for variable assignments
=============================================

## SYNOPSIS

`getdef [-v] [-e <path-to-exp-folder>] <file> <variable-name>`

## DESCRIPTION

`getdef` searches a given file for a variable assignment line of the form "animal=cat" where "animal" is the `<variable-name>`. Ignores "export animal=cat". `<file>` is the path to any file with variable definitions. If the variable is assigned in `~/.suites/overrides.def` getdef will show that value instead.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-e, <path-to-exp-folder>`: By default getdef will use `SEQ_EXP_HOME` as the experiment. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-v, --verbose`: Enable verbose debug output.

## EXAMPLES

```
getdef -e /home/smco500/.suites/rdps/r1 resources hr_start
```
