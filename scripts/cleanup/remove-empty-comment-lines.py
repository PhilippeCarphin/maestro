#!/usr/bin/python3

"""
Remove all lines like: '    #   ' or '#   ' from the target file. Overwrite.

Usage:
    remove-empty-comment-lines.py <path> [options]

Options:
    -h --help   Show this description.
"""

from docopt import docopt

def remove_empty(path):
    with open(path,"r") as f:
        lines=f.readlines()
    lines=[i for i in lines if i.strip()!="#"]
    data="".join(lines)
    with open(path,"w") as f:
        f.write(data)

def main(args):
    path=args["<path>"]
    remove_empty(path)
    print("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


