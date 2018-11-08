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
```

The build process uses the version or tags of your git repo to version the Maestro SSM package. If no tags (like 0.1.6) are present, it will use the first portion of the latest commit hash. This makes it difficult to release different Maestro SSM packages with the same version name. To see your current version:

```bash
git describe
```

If there are no tags, you'll need to either create one, or pull tags from the repo you originally cloned from:

```bash
git fetch --tags
```

The first compile may take awhile because of compiling Tcl and its libraries. However, if you create a shortcut called "_tcl" in the maestro folder (which points to a previous tcl compilation) you can speed up compilation a lot:

```bash
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

## Install

After the build process, you can install and publish the SSM package in the usual way. Here's a script you can copy paste:

```bash
cd maestro

VERSION=`./scripts/get_repo_version.py`
SSM_DOMAIN_PATH=$HOME/ssm/maestro/$VERSION
PLATFORM=ubuntu-14.04-amd64-64
SSM_PACKAGE=ssm/maestro_${VERSION}_${PLATFORM}.ssm

rm -rf $HOME/ssm/maestro/$VERSION
ssm created -d $SSM_DOMAIN_PATH
ssm install -f $SSM_PACKAGE -d $SSM_DOMAIN_PATH
ssm publish -p maestro_${VERSION}_${PLATFORM} -d $SSM_DOMAIN_PATH -pp $PLATFORM 
. ssmuse-sh -d $SSM_DOMAIN_PATH
```
