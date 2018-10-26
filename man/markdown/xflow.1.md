xflow -- visually monitor a Maestro experiment
=============================================

## SYNOPSIS

`xflow [-d <YYYYMMDDHH>] [-exp <exp-path>] [-noautomsg <0|1>] [-nosubmitpopup <0|1>] [-rc <maestro-rc-path>] [-n <node-path>] [-l <loop-arguments>] [-debug <0|1>]`

## DESCRIPTION

`xflow` is a Graphical User Interface that is used to monitor one experiment using the Maestro sequencer. 

The xflow command expects to be launched from within the path of an experiment. If not, the `-exp` option must be used. Typically a folder which is an experiment will contain the folders `resources`, `modules`, `logs`, and others.

For more information on Maestro experiments, see https://wiki.cmc.ec.gc.ca/wiki/Maestro/experiment

## OPTIONS

Some of these options can also be changed within the xflow graphical application, but are provided as command line options for convenience. Starting with the most commonly used:

* `-d <YYYYMMDDHH>`: These ten digits for year, month, day, and hour specify the times used when reading the logs and listings. If you provide a date from the past, then xflow will pretend it is that date and the progress, listings, and errors you see will be for that date. By default this will be the earliest date possible - often the date the suite was created.
* `-exp <path-to-exp-folder>`: By default xflow will assume the path it was launched from contains an experiment. Use this option to specify the experiment path instead. For example: `/home/smco500/.suites/rdps/r1`
* `-rc <maestro-rc-path>`: By default, Maestro is configured with the file found in your home: `~/.maestrorc`. You can ignore that file if you provide one here instead.
* `-noautomsg <0|1>`: By default, there will be automatic popups when the message center detects a message (for example, an error in a run). If this is set to 1, there will be no automatic popups.
* `-nosubmitpopup <0|1>`: By default, there will be an automatic popup when you submit a job in xflow. This also shows the command line equivalent for the command you just submitted. If this is set to 1, there will be no automatic popup.
* `-n <node-path>`: Highlight the given node.
* `-l <loop-arguments>`: (unknown)
* `-debug <0|1>`: Enable debugging mode and verbose command line output.

## EXAMPLES

If you used SSH to connect to the computer launching xflow, make sure you enable X11 forwarding with the `-X` SSH option.

Launch xflow for the RDPS, r1 experiment:

```
cd /home/smco500/.suites/rdps/r1
xflow
```

Launch xflow without cd by specifying the experiment path. Also, disable automatic message popups and use a custom maestrorc file.
q
```
xflow -exp /home/smco500/.suites/rdps/r1 -noautomsg 1 -rc ~/.maestrorc.2
```

Launch xflow and highlight the `main/assimcycle` node.

```
cd /home/smco500/.suites/rdps/r1
xflow -n /main/assimcycle
```

## AUTHOR

Maestro and its tools were written by the Canadian Meteorological Centre.

## REPORTING BUGS

Report xflow bugs to https://gitlab.science.gc.ca/maestro/maestro/issues

## COPYRIGHT

Maestro and its tools are licensed under GPL 2.1. This is free software: you are free to change and redistribute it.

## SEE ALSO

https://wiki.cmc.ec.gc.ca/wiki/Maestro

https://wiki.cmc.ec.gc.ca/wiki/Maestro/xflow

https://gitlab.science.gc.ca/maestro/maestro
