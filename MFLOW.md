`mflow` visualizes maestro suites and tasks like `xflow`, but purely as a commandline application. This project aims to be simple and fast, especially for remote work. With `mflow` you can:

* Visualize the flow of maestro tasks in a maestro experiment.
* Submit tasks, loops, loop members, and npass tasks.
* Set status (force status) to end/abort/init, etc.
* View success/abort/submit listings/logs.
* View or edit CFG/TSK/XML experiment files.
* Visually monitor the status of nodes.

Found a bug or have an idea? See the [contributing guide](/CONTRIBUTING.md) for how to help. Make sure to label `mflow` issues with the [mflow GitLab label](https://gitlab.science.gc.ca/CMOI/maestro/issues?label_name%5B%5D=component%3Amflow).

![alt text](/doc/gdps-g0-0.4.png)

# Try it out

First make sure to `ssmuse` the [maestro](https://gitlab.science.gc.ca/cmoi/maestro) SSM package to get `mflow`.

```bash
cd /home/smco500/.suites/gdps/g0
mflow
```

Use the keyboard to navigate to a node, and press enter. See `mflow -h` for more options and keyboard commands.

# Software Design

This project aims to be simple, tested, fast, and lightweight. This means:

* No dependencies on files outside the `mflow` folder.
* No dependencies on CMC specific environments or executables.
* Developers use [TDD](https://en.wikipedia.org/wiki/Test-driven_development) and the test suite to add, edit, and test during development.
* `mflow` runs and its tests pass on standard Linux environments outside internal work networks.
* All Python 3, aside from utility scripts for developers.

Additionally, the MaestroExperiment class in `maestro_experiment.py` is a solid generic base for any other Python 3 maestro utilities.

# Setup

```bash
git clone git@gitlab.science.gc.ca:CMOI/maestro.git
cd maestro/src/mflow
setup/install-dependencies.sh
```

# See Also

* [Maestro GitLab issues for mflow](https://gitlab.science.gc.ca/CMOI/maestro/issues?label_name%5B%5D=component%3Amflow).
* History: [mflow-prototype GitLab](https://gitlab.science.gc.ca/CMOI/mflow-prototype) and [original request for CLI xflow](https://gitlab.science.gc.ca/CMOI/maestro/issues/122).
* [Maestro](https://gitlab.science.gc.ca/CMOI/maestro)
