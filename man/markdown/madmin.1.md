madmin -- launch at most one Maestro server on a remote machine
=============================================

## SYNOPSIS

`madmin [-i] [-l] [-t] [-s] [-c <directive-xml>] [-r <dependency-item>]`

## DESCRIPTION

`madmin` send commands to the maestro server `mserver`. You can check the server status, list dependencies, remove dependencies, and shut down the server.

For more information on Maestro, see: https://wiki.cmc.ec.gc.ca/wiki/Maestro

## OPTIONS

* `-i:` Ask mserver if it is alive or inactive.
* `-l:` List all registered dependencies.
* `-m <mserver-machine>`: By default madmin will launch mserver on the local machine (`$TRUE_HOST`). Use this option to choose a different machine to launch mserver.
* `-v`: Enable verbose debug output.

## EXAMPLES

Launch mserver on eccc-ppp1:

```
madmin -m eccc-ppp1
```
