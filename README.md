Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems. 

## Community

* See the [Maestro article](https://wiki.cmc.ec.gc.ca/wiki/Maestro) in the CMC wiki.
* Chat with Maestro users and developers on the gccollab chat [Maestro group](https://message.gccollab.ca/channel/maestro).

## Contributing

Do you have a bug to report, feature request, or want to write and review code? See the [contributing guide](CONTRIBUTING.md).

Developers can contribute changes to the git repo using [this git branching model](https://nvie.com/posts/a-successful-git-branching-model/). In summary:

* Create release branches named `release-*` like `release-1.6`.
* Create feature branches named `add-button-xyz-to-abc-window`.
* Submit [merge requests](https://www.youtube.com/watch?v=0AT7JxqoIps&list=PLRf-PfhVvwFA7tGxwEgxgnJIY7aVevqqo&index=5) when your branch is ready.

## History

Maestro has a long development history. Let the maintainers know if you have any ideas on how to modernize, standardize, or simplify the codebase.

## Tcl / Tk

Tcl and Tk are used for the user interfaces of Maestro tools. Tcl is a general purpose programming language, and Tk is a GUI toolkit.

## Build, Install, Use

There are three steps to share a new Maestro version.

* Build: developers use the source code to compile executables and create an installer file - an SSM package.
* Install: system administrators use an SSM package to unpack the files to any location, and make it available for use.
* Use: users run `ssmuse-sh` to use an installed SSM package to their environment so that they can use it.

### Build

This first step will create an install file - an SSM package - for Maestro. To install and use the package, See the `Install` section.

To compile Maestro and create an SSM package simply use the makefile by typing:

```bash
 make
```

If you want the build to have a specific version label:

```bash
make VERSION=1.6-rc4
```

If no `VERSION` is provided, the build process uses the version or tags of your git repo to version the Maestro SSM package. If no tags (like 0.1.6) are present, it will use the first portion of the latest commit hash. This makes it difficult to release different Maestro SSM packages with the same version name. To see your current version:

```bash
git describe
```

If there are no tags, you'll need to either create one, or pull tags from the repo you originally cloned from:

```bash
git fetch --tags
```

The first compile may take awhile because of compiling Tcl and its libraries. At this time, running make on Tcl always recompiles all files which is slow.

### Install

After the build process, you can install and publish the SSM package in the usual way. If you're unfamiliar with installing SSM packages, the `reinstall-ssm.sh` script can get you started. Note: this will delete all files in the `<ssm-root>` folder, by default this is `$HOME/ssm/maestro`:

```bash
cd maestro
./ssm/reinstall_ssm.sh 1.6-rc4
```

You can also specify the `<ssm-root>` folder:

```bash
cd maestro
./ssm/reinstall_ssm.sh 1.6-rc4 --ssm-root=$HOME/tmp/dev4/ssm
```

See the top of the `reinstall_ssm.sh` file for all options.

### Use

After you or a system administrator has installed and published an SSM package, anyone on the network can use it. Some examples:

```
. ssmuse-sh -d ~/ssm/maestro/ad02f5g2/

. ssmuse-sh -d ~/ssm/maestro/1.5.1/

. ssmuse-sh -d eccc/cmo/isst/maestro/1.5.1-rc22
```

For more information on your environment setup see: https://wiki.cmc.ec.gc.ca/wiki/HPCS/ordenv
