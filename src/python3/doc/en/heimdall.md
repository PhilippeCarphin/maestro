[(French)](../fr/heimdall.md)

Heimdall is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues.

# Codes

What cases can `heimdall` detect?

* Critical errors like: missing EntryModule, suite folders like 'listings' have bad permissions or are missing.
* Errors like: dependency does not exist, bad XML, dissemination state does not match context.
* Warnings like: unused maestro files (tsk/cfg/xml), no support status in an operational suite, deprecated paths like `hall1`.
* Info like: maestro files (tsk/cfg/xml) are links to homes outside the project, git repo has uncommited changes, unknown nodelogger signals.
* Best practices like: hard coded or absolute dependency paths, very long support info, non-maestro files in maestro file (tsk/cfg/xml) folders.

And many more! See the [tab delimited CSV](csv/message_codes.csv) for every case. Each case has an automated test.

# Screenshots

![heimdall screenshot](/src/python3/screenshots/heimdall1.png)

# Try it out

```
~sts271/stable/bin/heimdall --exp=~smco500/.suites/gdps/g0 --level=i --max-repeat=2

cd /home/smco500/.suites/gdps/g0/listings/eccc-ppp3/main/intxfer_g0
~sts271/stable/bin/heimdall

~sts271/stable/bin/heimdall -h
```

# Development & Status

`heimdall` is available in `maestro` as of versions `1.7+`, though the latest development version can be found at `~sts271/stable/bin/heimdall`.

The project is spread out in two locations:

* The [sts271/heimdall repo](https://gitlab.science.gc.ca/sts271/heimdall/issues), created in 2018, containing a historic backlog of issues and ideas.
* The permanent home for `heimdall` in the `maestro` repo.

Once the historic backlog of issues and ideas in the [sts271/heimdall repo](https://gitlab.science.gc.ca/sts271/heimdall/issues) are mostly done, that project will be closed.

# Levels

Every `heimdall` message has a level: critical, error, warning, info, and best practice. For example `e003` or `c001`. The levels are based on whether tools like `xflow` and `mflow` can view and run the experiment.

The goal for all `heimdall` messages is that most people working on `maestro` projects agree with the standard.

### Critical \(c)

![color critical image](/src/python3/doc/color-critical.png)

Critical errors prevent the viewing or launching of the entire experiment.

### Error (e)

![color error image](/src/python3/doc/color-error.png)

Errors likely prevent the viewing or launching of parts of the experiment.

### Warning (w)

![color warning image](/src/python3/doc/color-warning.png)

A warning message explains how something is technically correct, however it may cause problems or unexpected behaviour.

### Info (i)

![color info image](/src/python3/doc/color-info.png)

An info message identifies aspects of the experiment which are good to know for people with less experience with this experiment.

### Best Practice (b)

![color best practices image](/src/python3/doc/color-best-practice.png)

A best practice message suggests changes to the experiment so that it better follows [ISST](https://wiki.cmc.ec.gc.ca/wiki/ISST) standards and other industry standard practices. The goal is that most people working on `maestro` projects agree with these best practices.

# Project Structure

### Tests

```
cd maestro/src/python3/bin
./run_heimdall_tests
```

Every code in the [tab delimited messages CSV](csv/message_codes.csv) has at least one automated test. Suppose a new code `i999` is created. There must also be an example experiment that generates it in `maestro/src/python3/mock_files/suites_with_codes/i999` and optionally in `maestro/src/python3/mock_files/suites_without_codes/i999`. If this condition is not met, a supervisor test will fail.

### Utilities

Files in the root level of `maestro/src/python3/src/utilities` are generically useful in any Python project and can be copy pasted into new projects without modification.

### mflow

`heimdall` uses components of `mflow`, like the `MaestroExperiment` class. Rarely, development in `heimdall` involves changing `mflow` dependencies. In that case, it's good to run the `mflow` tests too:

```
cd maestro/src/python3/bin
./run_mflow_tests
```

The project structure and tests could be flattened/merged in some future release.

# Myth

In Norse mythology, Heimdall or Heimdallr is attested as possessing foreknowledge, keen eyesight and hearing, and keeps watch for invaders and the onset of Ragnarök. Heimdall sees all.

![heimdall avatar](/src/python3/screenshots/heimdall-avatar.jpg)
