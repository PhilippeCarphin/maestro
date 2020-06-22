Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues.

# Usage

```
cd ~smco500/.suites/gdps/g0
heimdall

# or
heimdall --exp=~smco500/.suites/gdps/g0
```

See the `-h` option for details commandline usage:

```
heimdall -h
```

# Levels

Every Heimdall message has a level: critical, error, warning, info, and best practice. For example `e3` or `c1`. The levels are based on whether tools like `xflow` and `mflow` can view and run the experiment.

### Critical (c)

Critical errors prevent the viewing or launching of the entire experiment.

### Error (e)

Errors likely prevent the viewing or launching of parts of the experiment.

### Warning (w)

A warning message explains how something is technically correct, however it may cause problems or unexpected behaviour.

### Info (i)

An info message identifies aspects of the experiment which are good to know for people with less experience with this experiment.

### Best Practice (b)

A best practice message suggests changes to the experiment so that it better follows [ISST](https://wiki.cmc.ec.gc.ca/wiki/ISST) standards and other industry standard practices.












