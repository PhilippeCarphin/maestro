Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems. 

## Resources and Communities

* See the [Maestro article](https://wiki.cmc.ec.gc.ca/wiki/Maestro) in the CMC wiki.
* Chat with Maestro users and developers on the gccollab chat [Maestro group](https://message.gccollab.ca/channel/maestro).

## History

Maestro has a long development history. Let the maintainers know if you have any ideas on how to modernize, standardize, or simplify the codebase.

## Tcl / Tk

Tcl and Tk are used for the user interfaces of Maestro tools. Tcl is a general purpose programming language, and Tk is a GUI toolkit.

## Build

To compile Maestro and create an SSM package simply use the makefile by typing:

```bash
 make

# The first compile may take awhile because of compiling Tcl and its libraries.
# However, if you create a shortcut called "_tcl" in the maestro folder 
# (which points to a previous tcl compilation) you can speed up compilation a lot:

 cd maestro
 
 # This make will be slow
 make
 
 # Copy the results of the build process
 cp -r src/tcl ../tcl-maestro-backup-compiled
 ln -s ../tcl-maestro-backup-compiled _tcl
 
 # This make will be faster
 make
```

You have to move **tcl-maestro-backup-compiled** to somewhere outside the root Maestro folder, as the make process may delete build files for a clean make.

This system, and the Tcl dependencies, are being reconsidered.
