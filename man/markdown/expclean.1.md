expclean -- cleanup sequencing, logs, stats, and listings
=============================================

## SYNOPSIS

`expclean [-e <experiment>] [-t <days>] [-d <datestamp>] [-m <machine>] [-v] [-l]`

## DESCRIPTION

`expclean` cleans the various log files from an experiment based on a time or date. This may apply to the `sequencing`, `logs`, `stats`, and `listings` folders. If `-l` is given, also cleans logs. If `-m` is given, cleans files on that target machine, or `-m all` for all machines. If `SEQ_EXP_HOME` is not defined, `-e` must be given. The options `-d` and `-t` can be used together and both operations will be performed.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

### FOLDERS

`sequencing`

The `-d` option will delete files in `sequencing` with filenames containing the datestamp. The `-t` option deletes files directly inside `sequencing/status`, `sequencing/status/depends`, and `sequencing/status/remote_depends` (not recursively). `-t` also deletes matching files in the `sequencing` folder recursively but starting at a minimum depth of 2.

`logs`

The `-d` option with `-l` deletes the files `logs/$<datestamp>_nodelog` and `logs/$<datestamp>_toplog`. The `-t` option with `-l` deletes files directly inside `logs` (not recursively).

`stats`

The `-d` option with `-l` deletes the files `stats/<datestamp>` and `stats/<datestamp>_avg`. The `-t` option with `-l` deletes files directly inside `stats` (not recursively).

`listings`

All files in `listings/<machine>` are deleted according to the `-d` or `-t` rule.

## OPTIONS

Starting with the most commonly used:

* `-e <experiment>`: By default expclean will clean the experiment found in `SEQ_EXP_HOME`. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-t <days>:` Delete files older than this number of days (based on file modification date). `-t` can only be used on Linux systems, although target machines can be non-Linux.
* `-l:` Also delete some logs and stats. How this is done depends on whether the `-d` or `-t` options were used.
* `-d <YYYYMMDDHHMMSS>`: Delete files with filenames containing this datestamp. The datestamp is padded with zeroes to always be 14 digits if you only provide YYYYMMDD.
* `-m <machine>:` The target machine to delete the files. By default, uses `$TRUE_HOST`, your current machine. If `all` is provided for `<machine>`, then apply most rules to the machines found in the `listings` folder.
* `-v:` Verbose.

## EXAMPLES

Delete all the files and logs related to the 20130304000000 datestamp in the experiment found in `$SEQ_EXP_HOME`.

```
echo $SEQ_EXP_HOME
expclean -d 20130304000000 -l
```

Search the listings folder for all machines. Delete the `sequencing`, `logs`, `stats`, and `listings` which are older than 3 days or whose filenames contain `20130304000000`. Perform this action for all machines found in `listings` for the experiment found in `~smco500/.suites/rewps/forecast`

```
expclean -t 3 -d 20130304 -m all -l -e ~smco500/.suites/rewps/forecast
```
