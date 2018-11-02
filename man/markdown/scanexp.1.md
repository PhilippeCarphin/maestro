scanexp -- a simple way to search experiments for strings
=============================================

## SYNOPSIS

`scanexp -e <path-to-experiment> -s <string-to-search-for> [-ivl] [-f <filter-whitelist>]`

## DESCRIPTION

`scanexp` is essentially an enhanced grep, with defaults and options convenient for searching Maestro experiments.

scanexp requires either the `-e` option or the `SEQ_EXP_HOME` environment variable set to the experiment you want to scan. It also requires the `-s` option which is the string to search for.

For more information on Maestro experiments, see https://wiki.cmc.ec.gc.ca/wiki/Maestro/experiment

For more information on Maestro, see https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-e <path-to-exp-folder>`: By default scanexp will search the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-s <string-to-search-for>`: Simply, the string to search for in all experiment files.
* `-f <filter-whitelist>`: Use search filters, for example `-f cfg,res`. If this option is used, only search those file types. Available filters are: `cfg`, `module`, `task`, `log`, `res`, `bin`, `listing`. If no filter is provided, all files are searched except `log` and `listing`. There are some exceptions to how the search is performed. For a more detailed understanding of this logic, unfortunately you'll have to examine the script.
* `-i`: Use a case insensitive search.
* `-l`: Also search in listings. These logs are lengthy in live experiments, so this option may take awhile.
* `-v`: Enable verbose debug output, showing the actual bash commands use in the search.

## EXAMPLES

Search the experiment found in the present working directory for "hrdps_contingence":

```
scanexp -s hrdps_contingence -e `pwd`
```

Search the rewps/forecast experiment for the case insensitive string "turtle", and only search configuration and log files.

```
scanexp -s TURTLE -e ~smco500/.suites/rewps/forecast -i -f cfg,log
```
