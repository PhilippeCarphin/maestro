Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems. 

## Resources and Communities

* See the [Maestro article](https://wiki.cmc.ec.gc.ca/wiki/Maestro) in the CMC wiki.
* Chat with Maestro users and developers on the gccollab chat [Maestro group](https://message.gccollab.ca/channel/maestro).

## History

Maestro has a long development history. Let the maintainers know if you have any ideas on how to modernize, standardize, or simplify the codebase.

## Tcl / Tk

Tcl and Tk are used for the user interfaces of Maestro tools. Tcl is a general purpose programming language, and Tk is a GUI toolkit.

## Build, Install, Use

There are three steps to share a new Maestro version.

* Build: developers use the source code to create an installer file - an SSM package.
* Install: system administrators use an SSM package to unpack the files to any location, and make it available for use.
* Use: users run `ssmuse-sh` to use an installed SSM package to their environment so that they can use it.

### Build

This first step will create an install file - an SSM package - for Maestro. To install and use the package, See the Install section.

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
 # Replace ${SSM_PACKAGE} with the folder created by "make". Example: maestro_a0c8517c_ubuntu-14.04-amd64-64
 cp -r build/${SSM_PACKAGE}/src/tcl ../tcl-maestro-backup-compiled
 ln -s ../tcl-maestro-backup-compiled _tcl
 
 # This make will be faster
 make
```

You have to move **tcl-maestro-backup-compiled** to somewhere outside the root Maestro folder, as the make process may delete build files for a clean make.

This system, and the Tcl dependencies, are being reconsidered.

### Install

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
echo ". ssmuse-sh -d $SSM_DOMAIN_PATH"
```

### Use

After you or a system administrator has installed and published an SSM package, anyone on the network can use it. Some examples:

```
. ssmuse-sh -d ~/ssm/maestro/ad02f5g2/

. ssmuse-sh -d ~/ssm/maestro/1.5.1/

. ssmuse-sh -d eccc/cmo/isst/maestro/1.5.1-rc22
```

Note that the last line in the previous `Install` section will echo (output) the appropriate `ssmuse-sh` line to use your package:

```
echo ". ssmuse-sh -d $SSM_DOMAIN_PATH"
```

For more information on your environment setup see: https://wiki.cmc.ec.gc.ca/wiki/HPCS/ordenv
