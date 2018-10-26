expbegin -- submit the root of an experiment with special logging
=============================================

## SYNOPSIS

`expbegin [-e exp] [-d <YYYYMMDDhhmmss>] [-v]`

## DESCRIPTION

`expbegin` starts the root task of an experiment using the `maestro` command. It also enables special logging for this "begin" submission.

In a Maestro experiment, the expbegin log file `logs/log_expbegin` shows configuration and system information when the experiment began, like the location of the executables `nodeinfo`, `tictac`, and `maestro` used to run the experiment, as well as the submit date and submit command used. This information is appended by `expbegin` so that users can investigate the execution history of experiments.

For more information on Maestro, see https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-e <path-to-exp-folder>`: By default expbegin will begin the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-d <YYYYMMDDhhmmss>:` Launch a cron to submit on this 14 character date. Example: `20080530000000`. Anything shorter will be padded with zeroes. The default value is the date of the experiment. A date earlier than now will submit immediately.
* `-v:` Verbose. Equivalent to `set -x` in bash.

## EXAMPLES

Begin the RDPS, r1 experiment on the date 2020/01/01.

```
expbegin -e /home/smco500/.suites/rdps/r1 -d 20200101000000
```

## AUTHOR

Maestro and its tools were written by the Canadian Meteorological Centre.

## REPORTING BUGS

Report maestro bugs to https://gitlab.science.gc.ca/maestro/maestro/issues

## COPYRIGHT

Maestro and its tools are licensed under GPL 2.1. This is free software: you are free to change and redistribute it.

## SEE ALSO

https://wiki.cmc.ec.gc.ca/wiki/Maestro

https://gitlab.science.gc.ca/maestro/maestro
