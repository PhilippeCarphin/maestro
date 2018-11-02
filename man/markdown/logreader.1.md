logreader -- analyse Maestro logs and output tsv elements for tcl
=============================================

## SYNOPSIS

`logreader [-i <input-file>] [-t type] [-o <output-file>] [-n <days-for-average>] [-e <experiment-path>] [-d <datestamp>] [-v] [-c]`

## DESCRIPTION

`logreader` reads the files in `$SEQ_EXP_HOME/logs`, computes statistics on them, prints the results as `tsv` elements (thread shared variables) for tcl, and writes to `$SEQ_EXP_HOME/stats`. The tsv output is not human readable - instead it is an intermediate step used internally in Maestro's visualisation tools like `xflow`. The output includes averages for the end, beginning, submission delay, and progress for all the nodes of an experiment.

This tool outputs tsv elements because often multiple threads will need access to this data at the same time. tsv elements allow this. The output is separated by newlines. The first line shows statuses: 

`{ exectime 00:00:16 submitdelay 00:00:11 submit 20181101.05:04:55 begin 20181101.05:05:06 end 20181101.05:05:22 deltafromstart 00:15:18 } +2 { exectime 00:00:16 submitdelay 00:00:09 submit 20181101.05:03:30 begin 20181101.05:03:39 end 20181101.05:03:55 deltafromstart 00:13:51 } +5     ... (more)`

The second line shows averages:

`{ exectime 00:00:14 submitdelay 00:00:09 submit 05:07:07 begin 05:07:18 end 05:07:32 deltafromstart 00:17:28 } +20 { exectime 00:00:14 submitdelay 00:00:09 submit 05:08:34 begin 05:08:45 end 05:09:00 deltafromstart 00:18:57 } +18     ... (more)`

and the third line shows read offsets:

`last_read_offset 327498`

As for the files written to `$SEQ_EXP_HOME/stats` with the `-o` option, the format is more human readable:

`SEQNODE=/rewps/prog/loop_run:MEMBER=+17:SUBMIT=20181101.04:52:01:BEGIN=20181101.04:52:02:END=20181101.05:04:12:EXECTIME=00:12:10:SUBMITDELAY=00:00:01:DELTAFROMSTART=00:14:08     ... (more)`

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-i <input-file>:` Specify a logfile to read. If no `-i` is provided, logreader will use `${SEQ_EXP_HOME}/logs/${datestamp}_nodelog`.
* `-o <output-file>:` Specify an output file for the computed statistics in a more human readable form. For example:
* `-t <filter-type>:` Filter results by type. Available filters are: `log` which shows statuses and stats used by xflow. `statuses`, `stats`, `avg`, and `compute_avg`. Default is `log`.
* `-n <days-for-average>:` Specify a number of days since `<datestamp>` for averaging. Used with `-t avg`. Default value is 7 days. This is a 10% truncated average to account for extremes.
* `-c:` If the output file already exists, write nothing to that file.    
* `-d <YYYYMMDDhhmmss>:` The 14 character date you want to examine. Example: `20080530000000`. Anything shorter will be padded with zeroes. The default value is the date of the experiment.
* `-e <experiment-path>:` By default the logreader uses `$SEQ_EXP_HOME`. For example: `-e /home/smco500/.suites/rdps/r1`
* `-v:` Set verbose code tracing.

## EXAMPLES

The best way to see an up to date technical use of `logreader` in the Maestro project is to search for it in the source code. For example:

```
cd maestro
grep -rn "logreader -e" .
```

This command will read the logs for the REWPS forecast experiment for November 2018:

```
logreader -d 20181101000000 -e ~smco500/.suites/rewps/forecast
```

Read the logs for `$SEQ_EXP_HOME` and create a statistics file in the default `-o` location `$SEQ_EXP_HOME/stats/20181101000000`:
        
```
logreader -d 20181101000000 -t stats
```

Read the logs for `$SEQ_EXP_HOME` and create an averages statistics file in the default `-o` location `$SEQ_EXP_HOME/stats/20181101000000_avg`. Use the past 14 days instead of the default:
        
```
logreader -d 20181101000000 -t avg -n 14
```
