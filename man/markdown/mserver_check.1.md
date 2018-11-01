mserver_check -- launch at most one Maestro server on a remote machine
=============================================

## SYNOPSIS

`mserver_check -m [<mserver-machine>]`

## DESCRIPTION

`mserver_check` launches mserver if mserver is not running. The `-m` option is not really an option as it must be provided. If `<mserver-machine>` is not provided, mserver_check will use `$TRUE_HOST` by default, for example `eccc-ppp1`. mserver_check does this by running a command remotely using SSH, so it requires your SSH authorized keys to bet setup.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

* `-m <mserver-machine>`: By default mserver_check will launch mserver on the local machine (`$TRUE_HOST`). Use this option to choose a different machine to launch mserver.
* `-v`: Enable verbose debug output.

## EXAMPLES

Launch mserver on eccc-ppp1:

```
mserver_check -m eccc-ppp1
```

If `$TRUE_HOST` is `eccc-ppp1`, the previous command is equivalent to this command:

```
mserver_check -m
```
