
import sys
import os

suffix = sys.argv[1]
folder = sys.argv[2]
filename = "turtle-burp-"+suffix+".txt"
path = folder+os.sep+filename

if os.path.isdir(folder):
    with open(path, "w") as f:
        f.write("turtle burp! suffix="+suffix)
else:
    sys.exit(1)
