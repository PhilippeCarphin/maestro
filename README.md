Maestro is a suite of tools which organize, visualize, schedule, validate, and submit tasks to computer systems. 

## Tools

Here are some of the main tools in the Maestro suite:

* [xflow](https://wiki.cmc.ec.gc.ca/wiki/Maestro/xflow) monitors and visualizes a single experiment created by Maestro.
* [mflow](https://wiki.cmc.ec.gc.ca/wiki/Maestro/mflow) is a simple and fast alternative to xflow, especially good for remote work.
* [xflow_overview](https://wiki.cmc.ec.gc.ca/wiki/Maestro/xflow_overview) monitors and visualizes many experiments created by Maestro.
* The [sequencer](https://wiki.cmc.ec.gc.ca/wiki/Maestro/sequencer) manages the sequenced execution of task nodes.
* [xm](https://wiki.cmc.ec.gc.ca/wiki/Maestro/xm) is a visual tool used to create new Maestro experiments.
* [heimdall](src/python3/HEIMDALL.md) is a maestro suite scanner. Scan for errors, warnings, recommendations, and installation issues.
* Finally, many commandline tools. As of version `1.8.0` you can type `m. <tab> <tab>` to see a list of most maestro commandline tools.

## Community & Resources

* See the [Maestro article](https://wiki.cmc.ec.gc.ca/wiki/Maestro) in the CMC wiki.
* Chat with Maestro users and developers on the gccollab chat [Maestro group](https://message.gccollab.ca/channel/maestro).
* Review the [Linux man pages for most of the maestro commandline tools](https://wiki.cmc.ec.gc.ca/wiki/Maestro/man_pages) or view the pages as [markdown files](https://gitlab.science.gc.ca/CMOI/maestro/tree/master/man/markdown).

## Contributing

Do you have a bug to report, feature request, or want to write and review code? See the [contributing guide](CONTRIBUTING.md).

Developers can contribute changes to the git repo roughly using [this git branching model](https://nvie.com/posts/a-successful-git-branching-model/). In summary:

* Create a new issue describing the feature or bug before doing any work.
* Create feature branches named `feature-xflow-refresh-button` with all commits for that feature.
* Create bugfix branches named `bugfix-empty-catchup-xml` with all commits for that bugfix.
* Submit [merge requests](https://www.youtube.com/watch?v=0AT7JxqoIps&list=PLRf-PfhVvwFA7tGxwEgxgnJIY7aVevqqo&index=5) when your branch is ready. Start the title of the merge request with "WIP" for "work in progress" if it's not ready to merge, but you want feedback.
* Release branches named `release-*` like `release-1.6` can be used to cherry-pick hotfixes and publish another SSM, without releasing a new major version.

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
make VERSION=1.6-dev5
```

If no `VERSION` is provided, the build process uses the version or tags of your git repo to version the Maestro SSM package. If no tags (like 1.6.0) are present, it will use the first portion of the latest commit hash. This makes it difficult to release different Maestro SSM packages with the same version name. To see your current version:

```bash
git describe
```

If there are no tags, you'll need to either create one, or pull tags from the repo you originally cloned from:

```bash
git fetch --tags
```

### Install

After the build process, you can install and publish the SSM package in the usual ways. If you're unfamiliar with installing SSM packages, the `install-ssm.sh` script is a convenient shortcut:

```bash
cd maestro/ssm

# Simple example
./install_ssm.sh 1.6.3

# To see usage help and more options
./install_ssm.sh -h
```

### Use

After you or a system administrator has installed and published an SSM package, anyone on the network can use it. Some examples:

```
. ssmuse-sh -d ~/ssm/maestro/ad02f5g2/

. ssmuse-sh -d ~/ssm/maestro/1.5.1/

. ssmuse-sh -d eccc/cmo/isst/maestro/1.5.1-rc22
```

For more information on your environment setup see: https://wiki.cmc.ec.gc.ca/wiki/HPCS/ordenv
