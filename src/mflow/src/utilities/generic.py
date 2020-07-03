"""
The contents of this script are generally useful and can be copied, without modification, to other python projects.
"""

import os
import gzip
import os.path
from utilities.colors import print_green
from utilities.path import get_matching_paths_recursively

def get_change_time(path):
    try:
        return os.path.getctime(path)
    except FileNotFoundError:
        return "<FileNotFoundError>"
    except PermissionError:
        return "<PermissionError>"
    except OSError:
        "this may occur because of infinitely nested soft links"
        return "<OSError>"

def insert_into_dictionary(a,b):
    """
    If a key in dictionary 'b' is not in 'a', insert its key/value into 'a'.
    """
    for key,item in b.items():
        if key not in a:
            a[key]=b[key]

def get_distance(x1,x2,y1,y2):
    "returns float cartesian distance between two points"
    x=abs(x1-x2)
    y=abs(y1-y2)
    return (x**2+y**2)**0.5

def get_key_value_from_path(key,path):
    """
    If key is 'ABC' and file at path contains "ABC=123" returns "123".
    """
    if not os.path.isfile(path):
        return ""
    with open(path,"r") as f:
        return get_key_value_from_text(key,f.read())

def get_key_value_from_text(key,text):
    """
    If key is 'ABC' and text contains "ABC=123" returns "123".
    """
    lines=text.split("\n")
    for line in lines:
        if line.strip().startswith(key) and "=" in line:
            return line.split("=")[-1].strip()
    return ""

def recursive_replace_in_files(before,after,folder):
    "replaces all instances of 'before' with 'after', in all files found in path, recursively"
    if not os.path.isdir(folder):
        return
    for path in get_matching_paths_recursively(folder):
        try:
            with open(path,"r") as f:
                data=f.read()
            data=data.replace(before,after)
            with open(path,"w") as f:
                f.write(data)
        except (UnicodeDecodeError, FileNotFoundError, OSError):
            pass

def get_variable_value_from_file(path,name):
    """
    If name is "FRONTEND"
    finds the first line like "FRONTEND=123" and returns "123"
    """
    
    try:
        with open(path,"r") as f:
            lines=f.readlines()
    except:
        lines=[]
        
    for line in lines:
        if line.startswith(name+"="):
            return line[line.index("=")+1:].strip()
    
    return ""

def superstrip(text,chars):
    """
    Like Python strip, except uses the characters in the
    list/string 'chars' instead of just whitespace.
    """
    start_index=0
    end_index=len(text)-1
    for i,c in enumerate(text):
        if c not in chars:
            start_index=i
            break
    for i,c in enumerate(reversed(text)):
        if c not in chars:
            end_index=len(text)-i
            break
    
    return text[start_index:end_index]

def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)

def safe_get_lines(path):
    """
    Opens plaintext or gzipped files, trying to handle weird encoding gracefully.
    Get all lines from a file which can be decoded. Ideally, all of them.
    This function should never raise an exception - instead add exception handling for specific exceptions as they pop up.
    """

    if is_gzipped(path):
        read_mode="rt"
        open_function=gzip.open
    else:
        read_mode="r"
        open_function=open
    
    encodings=("utf-8","latin-1")
    for encoding in encodings:
        try:
            with open_function(path,read_mode,encoding=encoding,errors="ignore") as f:
                return f.readlines()
        except UnicodeDecodeError:
            pass
        
    return []

def reverse_readlines(path, buf_size=8192, encoding="utf-8"):
    """
    A generator that returns the lines of a file in reverse order.
    Effective for reading just the end of big files.
    
    From:
        https://stackoverflow.com/a/23646049
    """
    with open(path,encoding=encoding) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment

def safe_write(path,data,verbose=True):
    "Writes this data to path, creates any necessary folders."
    directory=os.sep.join(path.split(os.sep)[:-1])
    if directory and not os.path.exists(directory):
        if verbose:
            print_green("Making directory: '%s'"%directory)
        os.makedirs(directory)
    with open(path,"w") as f:
        f.write(data)
    if verbose:
        print_green("Wrote data to file '%s'"%path)

def is_gzipped(path):
    """
    Returns true if gzipped.
    Unfortunately this slow method may be the only reliable one.
    """
    try:
        with gzip.open(path,"rt",encoding="utf-8") as f:
            f.read()
            return True
    except:
        return False
