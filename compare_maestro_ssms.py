#!/usr/bin/python3
"This script shows the contents and differences between my Maestro ssm folders and an official Maestro ssm folders."

import os.path, sys
from colors import *

my_ssm="/home/sts271/ssm/maestro/1.5.1"
official_ssm="/fs/ssm/eccc/cmo/isst/maestro/1.5.1-rc22"

try:
    a=os.listdir(my_ssm)
except FileNotFoundError:
    print_yellow("Not a folder: '%s'"%my_ssm)
    sys.exit()

try:
    b=os.listdir(official_ssm)
except FileNotFoundError:
    print_yellow("Not a folder: '%s'"%official_ssm)
    sys.exit()

c=list(set(a).difference(set(b)))
d=list(set(b).difference(set(a)))

def print_sort(label,items,path=""):
    if not items:
        return
    spaces="      "
    print_green("\n"+label.upper()+":")
    if path:
        print_yellow("Path = '%s'"%path)
    print(spaces+("\n"+spaces).join(sorted(items)))

print_sort("My SSM",a,my_ssm)
print_sort("Official SSM",b,official_ssm)
print_sort("Only found in my SSM:",c)
print_sort("Only found in official SSM:",d)
if not c and not d:
    print_green("\nNo differences found between the two lists.\n")
