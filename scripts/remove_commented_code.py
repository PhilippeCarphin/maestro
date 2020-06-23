#!/usr/bin/python3

"""
Strip out all commented code from a target source code file. Interactively, answer yes or no if you want to remove each comment.

Where <language> can be:
    c

Example of commented code:

/*
if ( a == 2 ) {
*/
if ( a == 3 ) {



Usage:
    remove_commented_code.py <language> <source-code-file> [options]

Options:
    -h --help   Show this description.
"""

import re
import os.path
from utilities.docopt import docopt
from utilities.colors import print_orange, print_blue, print_green, print_red

def remove_c_commented_code(path):
    
    print("Reading '%s'"%path)
    
    with open(path,"r") as f:
        data=f.read()
    original_data=data
    lines=data.split("\n")
    lines=[i.strip() for i in lines]
    
    context_size=200
    change_count=0    
    to_remove=[]
    
    r=r"\/\*(\*(?!\/)|[^*])*\*\/"
    blocks=re.finditer(r,data,re.MULTILINE)
    block_count=len(re.findall(r,data,re.MULTILINE))
    
    for block_index,match in enumerate(blocks, start=1):
                
        context_min_index=max(0,match.start()-context_size)
        context_max_index=min(match.end()+context_size,len(original_data)-1)
        before_context=original_data[context_min_index:match.start()]
        after_context=original_data[match.end():context_max_index]
        line_number=original_data[:match.start()].count("\n")
        
        print("     %s\n"%path)
        print(before_context,end="")
        print_orange(match.group(0),end="")
        print(after_context)
        print_green("Line: %s of %s"%(line_number,len(lines)))
        print("Remove comment block %s of %s?"%(block_index,block_count))
        answer=input("[yn]: ")
        if answer=="y":
            change_count+=1
            data=data.replace(match.group(0),"")
            print_blue("Removed the comment block.")
        else:
            print_red("No. Did not remove this line. Some comments are good!")
    
    with open(path,"w") as f:
        f.write(data)
    print("Wrote %s changes to file '%s'"%(change_count,path))

def main(args):
    path=args["<source-code-file>"]
    language=args["<language>"]
    
    if not os.path.isfile(path):
        print("Not a file: '%s'"%path)
        return

    if language=="c":
        remove_c_commented_code(path)
    else:
        raise NotImplemented("Language: '%s'"%language)
    
    print("Done.")

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)


