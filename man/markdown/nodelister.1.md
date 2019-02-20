nodelister -- print selected listing logs associated to a Maestro node
=============================================

## SYNOPSIS

`nodelister -n <node> [-l <loop-arguments>] [-type <listing-type>] [-d <datestamp>] [-list] [-o <output-file>] [-f <list-file>]`

## DESCRIPTION

`nodelister` selects and prints activity logs (listings) for Maestro tasks. It searches the folders in `${SEQ_EXP_HOME}/listings`. To use nodelister, `SEQ_EXP_HOME` must be defined. For example, you might run this before using nodelister:

```
export SEQ_EXP_HOME=/home/smco500/.suites/rdps/r1
```

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## REQUIRED ARGUMENTS

You must use either `-n` or `-f`, not both.

* `-n <node>`: The full node name. Example: `/regional/assimilation/00/gen_cutoff`
* `-f <list-file>`: View a specific listing instead of latest. This requires the full path to the listing file.

## OPTIONS

Starting with the most commonly used:

* `-type <listing-type>`: Define the type of listing: `success`, `abort`, `submission`, `all`. Default is `success`, or `all` if `-list` is used.
* `-d <datestamp>`: The experiment datestamp in the form `YYYYMMDDhhmmss`. Default is the latest.
* `-list`: show all possible listings of the node.
* `-l <loop-arguments>`: A comma-separated list of loop arguments. Example: `outer_loop=1,inner_loop=2`
* `-o <output-file>`: Redirect all output to this file. Default value is `/tmp/nodelister_<process-id>`

## EXAMPLES

A great way to see examples of nodelister is to search an existing experiment for nodelister:

```
grep -rn "nodelister" ~smco500/.suites/gdps/
```

The following examples will get nodeinfo for "run_loop_on_hours_54" in the RDPS, r1 experiment for run 18. Show all the possible listings:

```
export SEQ_EXP_HOME=/home/smco500/.suites/rdps/r1
nodelister -n /main/cmdw_post_processing/blending/run/loop_on_hours_54 [-l loopargs] -type [success,abort,submission] -d datestamp -list 
```

Show the latest abort listing:

```
export SEQ_EXP_HOME=/home/smco500/.suites/rdps/r1
nodelister -n /main/cmdw_post_processing/blending/run/loop_on_hours_54 -type abort
```

Show the latest success listings and output to the dile `superduper.txt`:

```
export SEQ_EXP_HOME=/home/smco500/.suites/rdps/r1
nodelister -n /main/cmdw_post_processing/blending/run/loop_on_hours_54 -type success -o /home/sts271/tmp/superduper.txt
```
