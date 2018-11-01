mserver_check -- launch at most one Maestro server on a remote machine
=============================================

## SYNOPSIS

`mserver_check [-m <mserver-machine>]`

## DESCRIPTION

`mserver_check` launches mserver if mserver is not running. It the `-m` option is provided, it launches on that machine.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

Starting with the most commonly used:

* `-m <mserver-machine>`: By default mserver_check will launch mserver on the local machine (`$TRUE_HOST`). Use this option to choose a different machine to launch mserver.
* `-v`: Enable verbose debug output.

## EXAMPLES

Launch mserver on eccc-ppp1:

```
mserver_check -m eccc-ppp1
```
