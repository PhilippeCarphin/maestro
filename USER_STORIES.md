This document describes all critical user stories for Maestro. All user stories must be simple and clear enough that non-experts can run through them to test maestro. A user story identifies:

* The type of user who does this action. Example: suite developer
* The action they want to perform.
* The steps on how to do that action. Simple and clear, with concrete examples.
* The expected result.

= Make SSM from clean repo =

As a maestro developer, make and install the Maestro ssm from a clean repo.

```bash
# Note: these commands may need to be modified.
cd $HOME/tmp
git clone git@gitlab.science.gc.ca:CMOI/maestro.git
cd maestro
VERSION=1.6-dev1
make VERSION=$VERSION
./reinstall-ssm.sh $VERSION
. ssmuse-sh -d $HOME/ssm/maestro/$VERSION
which nodeinfo
```

Expected: The last `which` command should show the path of nodeinfo from your ssm install.

= xflow =
As a suite developer, launch xflow and submit a task from a personal suite.

```bash
cd ~/.suites/turtle
xflow
```

Expected: The task should be submitted, and eventually finish.

= xflow_overview =
As a meteorologist, launch xflow_overview on the operational suites.

```bash
xflow_overview -suites /home/smco500/.suites/gdps/g0
# double click a suite to also launch xflow
```

Expected: overview and xflow successfully launch.

= man pages =
As a newbie, launch a man page.

```bash
man xflow
```

Expected: A standard linux man page. Quit with `q`.
