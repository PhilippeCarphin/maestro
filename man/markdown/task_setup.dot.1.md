task_setup.dot -- run the task setup utility with your environment variables
=============================================

## SYNOPSIS

`task_setup.dot [arg1, arg2, arg3, ...]`

## DESCRIPTION

`task_setup.dot` runs the `task_setup.py` utility with your environment variables. You can also supply extra arguments to `task_setup.dot` which will be passed to `task_setup.py`.

## EXAMPLES

This example will send the current environment variables, and the `-v` option to the `task_setup.py` utility:

```
 . task_setup.dot -v
```

Note the required "." before `task_setup.dot`. This means that environment variables set without an export like "animal=cat" will be sent to `task_setup.dot` and thus `task_setup.py`. Otherwise, only "export animal=cat" variables are shared.

For a list of all `task_setup.py` options, run:

```
man task_setup.py
```
