xflow_overview -- visually monitor multiple Maestro experiments
=============================================

## SYNOPSIS

`xflow_overview [-exp <path-to-experiment-folder>] [-rc <maestro-rc-path>] [-logspan <integer-hours>] [-display <x-windows-display>] [-as <username>] [-debug <0|1>] [-noautomsg <0|1>] [-logfile <path-to-logfile>]`

## DESCRIPTION

`xflow_overview` is a Graphical User Interface that is used to monitor multiple experiments using the Maestro sequencer. Given a specific date, it will show a 24 hour view of all runs for a set of experiments. The visual information includes current status, errors, and execution length.

xflow_overview requires a suites XML file to launch. By default, it reads the file `~/xflow.suites.xml` unless the `-suites` option is given.

For more information on Maestro experiments, see https://wiki.cmc.ec.gc.ca/wiki/Maestro/experiment

## OPTIONS

Starting with the most commonly used:

* `-exp <path-to-experiment-folder>`: Launching xflow_overview for all experiments can be slow. Use this option instead to view a single experiment.
* `-rc <maestro-rc-path>`: By default, Maestro is configured with the file found in your home: `~/.maestrorc`. You can ignore that file if you provide one here instead.
* `-logspan <integer-hours>`: There is a limit to how far back in history xflow_overview searches in logs. This changes that limit. You could for example use `-logspan 72` to see logs and aborts reaching back three days.
* `-display <x-windows-display>`: Set the X windows display. By default it will be a local display device `localhost:53.0`.
* `-as <username>:` By default, xflow_overview will launch as the current user with its permissions for submitting jobs. Use this option to specify a different user. It may prompt for a password.
* `-debug <0|1>`: Enable debugging mode and verbose command line output.
* `-noautomsg <0|1>`: By default, there will be automatic popups when the message center detects a message (for example, an error in a run). If this is set to 1, there will be no automatic popups.
* `-logfile <path-to-logfile>`: Dump verbose debugging output to this logfile.

## EXAMPLES

If you used SSH to connect to the computer launching xflow_overview, make sure you enable X11 forwarding with the `-X` SSH option.

Launch xflow_overview for the RDPS, r1 experiment:

```
xflow -exp ~smco500/.suites/rdps/r1
```

Launch xflow_overview for all operational suites with debugging console output enabled and a different maestrorc file:

```
xflow_overview -suites ~smco500/xflow.suites.xml -debug 1 -rc ~/.maestrorc2
```
