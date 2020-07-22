#!/usr/bin/python3

"""
This script compares the executables in $PATH and environment variables in the shell before and after an ssmuse command.
This is a good way to compare a development ssm package to a stable version.

Usage:
    environment-compare.py <ssm-domain1> [<ssm-domain2>] [options]

Options:
    --no-color             Do not print colors, useful for capturing the output into files.
    --no-colour            See '--no-color'.
    --loader1=<command>    Use this command to load the package for domain1, like 'ssmuse-sh -d' or 'r.load.dot' [default: ssmuse-sh -d]
    --loader2=<command>    Use this command to load the package for domain2, like 'ssmuse-sh -d' or 'r.load.dot' [default: ssmuse-sh -d]

    -h --help              Show this description.
"""

from utilities.docopt import docopt
from utilities.colors import print_yellow, print_green
from utilities.generic import safe_check_output
import os, sys, subprocess

def get_lines_from_cmd(cmd):
    output=safe_check_output(cmd)
    return set([i.strip() for i in output.split("\n")])

def compare_lines_from_commands(cmd1,cmd2):
    lines1=get_lines_from_cmd(cmd1)
    lines2=get_lines_from_cmd(cmd2)

    ab=sorted(list(lines1.difference(lines2)))
    ba=sorted(list(lines2.difference(lines1)))

    if set(ab)==set(ba):
        print_green("Results are the same.")
        return

    print_yellow("%s lines from '%s'"%(len(lines1),cmd1))
    print_yellow("%s lines from '%s'"%(len(lines2),cmd2))

    if ab:
        print("%s lines present in:"%len(ab))
        print_green("    "+cmd1)
        print("but not:")
        print_green("    "+cmd2)

    for line in ab:
        print(line)

    if ba:
        print("%s lines present in:"%len(ba))
        print_green("    "+cmd2)
        print("but not:")
        print_green("    "+cmd1)

    for line in ba:
        print(line)

def main(args):
    domain1=args["<ssm-domain1>"]
    domain2=args["<ssm-domain2>"]
    loader1=args["--loader1"]
    loader2=args["--loader2"]

    if args["--no-color"] or args["--no-colour"]:
        global print_yellow
        global print_green
        print_yellow=print
        print_green=print

    cmd1=". %s %s ; env ; compgen -c"%(loader1,domain1)
    cmd2=". %s %s ; env ; compgen -c"%(loader2,domain2)

    print_yellow("\nComparing fresh environment to '%s'"%domain1)
    compare_lines_from_commands("env ; compgen -c",cmd1)
    
    if domain2:
        if loader1==loader2:
            print_yellow("\nComparing '%s' to '%s'"%(domain1,domain2))
        else:
            print_yellow("\nComparing '%s' loaded with '%s' to '%s' loaded with '%s'"%(domain1,loader1,domain2,loader2))
        compare_lines_from_commands(cmd1,cmd2)


if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)
