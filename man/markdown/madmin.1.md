madmin -- send commands to a maestro server
=============================================

## SYNOPSIS

`madmin [-i] [-l <experiment-path>] [-t <experiment-path>] [-s] [-r <dependency>]`

## DESCRIPTION

`madmin` send commands to the maestro server `mserver`. You can check the server status, list dependencies, remove dependencies, and shut down the server.

The dependencies listed with the `-l` option are different from simple Maestro experiment dependencies. Instead, they may be cross-user (or deprecated OCM) dependencies. For example, smco501 experiments may depend on output from smco500 experiments.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

* `-i:` Ask mserver if it is alive or inactive.
* `-l <experiment-path>:` List all registered dependencies for `<experiment-path>`. If `<experiment-path>` is not provided, use `$SEQ_EXP_HOME`. This searches for files written to the `maestrod` folder, for example: `smco500/.suites/maestrod/dependencies/polling/v1.5.1`. Often, this option prints nothing as these temporary dependency files are deleted once resolved by the maestro server.
* `-r <dependency>:` Remove registered dependencies. The value for `<dependency>` can either be a key found with the `-l` option, an experiment name, `all` which removes all registered dependencies for this user, or no value which removes registered dependencies in `$SEQ_EXP_HOME`.
* `-t <experiment-path>:` List experiments depending on this experiment. If `<experiment-path>` is not provided, use `$SEQ_EXP_HOME`.
* `-s:` Shut down the server.

## EXAMPLES

Print to console whether the maestro server is alive or inactive:

```
madmin -i
```

Print dependencies for the smco50`1` scribe_naefs suite:

```
madmin -l /home/smco501/.suites/scribe_naefs
```

For the above command, the output may show this dependency on smco50`0` naefs_foreign:

```
node=/matrices_scribe_naefs/matrices_scribe_ncep depend_on_exp=/home/smco500/maestro_suites/naefs_foreign node:/main/ncep/rawDaemon loop_args: key:875df30f4e287aa77a3f51bfeb85fba0
```
