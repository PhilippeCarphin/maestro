import os
import re
from utilities.io import safe_read

"""
Matches:
    $ABC
    ${ABC}
"""
BASH_VARIABLE_OPTIONAL_CURLY_REGEX=re.compile("\\$({[\\w]+}|[\\w]+)")

"matches lines that declare a bash variable, group(1) is the variable name"
BASH_VARIABLE_DECLARE_REGEX=re.compile("^[ \t]*([a-zA-Z]+[a-zA-Z0-9_]*)[ ]*=")

"matches lines that declare a bash variable, with optional 'export' "
BASH_VARIABLE_DECLARE_REGEX_WITH_EXPORT=re.compile("^[ \t]*(export )?[a-zA-Z]+[a-zA-Z0-9_]*[ ]*=")

def remove_chars_in_text(chars,text):
    """
    Return text where all chars have been removed.
    """
    for c in chars:
        text=text.replace(c,"")
    return text

def superstrip(text, chars):
    """
    Like Python strip, except uses the characters in the
    list/string 'chars' instead of just whitespace.
    """
    start_index = 0
    end_index = len(text)-1
    for i, c in enumerate(text):
        if c not in chars:
            start_index = i
            break
    for i, c in enumerate(reversed(text)):
        if c not in chars:
            end_index = len(text)-i
            break

    return text[start_index:end_index]

def get_key_values_from_path(path, include_export_lines=True):

    if not os.path.isfile(path):
        return {}

    text = safe_read(path)

    return get_key_values_from_text(text, include_export_lines)


def get_key_values_from_text(text, include_export_lines=True):
    """
    Given text with bash-like variable declares:
AAA=111
    BBB=222
    export CCC=333
export DDD=444
# GGG=111
    returns:
        {"AAA":"111","BBB":"222","CCC":"333","DDD":"444"}

    Ignore export lines if include_export_lines is false.
    """

    lines = text.split("\n")

    "select only var declare lines"
    if include_export_lines:
        var_regex = BASH_VARIABLE_DECLARE_REGEX_WITH_EXPORT
    else:
        var_regex = BASH_VARIABLE_DECLARE_REGEX

    lines = [line.strip() for line in lines if var_regex.search(line.strip())]
    data = {}
    for line in lines:
        name = line.split("=")[0]
        if include_export_lines and name.startswith("export "):
            name = name[7:]
        value = line[line.index("=")+1:]
        data[name.strip()] = value.strip()
    return data


def get_key_value_from_path(key, path):
    """
    If key is 'ABC' and file at path contains "ABC=123" returns "123".
    """
    if not os.path.isfile(path):
        return ""
    with open(path, "r") as f:
        return get_key_value_from_text(key, f.read())


def get_key_value_from_text(key, text):
    """
    If key is 'ABC' and text contains "ABC=123" returns "123".
    """
    lines = text.split("\n")
    for line in lines:
        if line.strip().startswith(key) and "=" in line:
            return line.split("=")[-1].strip()
    return ""

def strip_comments_from_text(text):
    """
    Return the text content of this string, minus any lines that are
    comments, like '#' in bash.
    """
    lines = text.split("\n")
    lines = [i for i in lines if not i.strip().startswith("#")]
    return "\n".join(lines)

def get_bash_variables_used_in_text(text,strip_comments=True):
    """
    Given text like:
        echo 123 $ABC ${CAT}
    returns:
        ["ABC","CAT"]
    """
    
    if strip_comments:
        text=strip_comments_from_text(text)
        
    variables=BASH_VARIABLE_OPTIONAL_CURLY_REGEX.findall(text)
    
    "strip curly brackets"
    variables=[superstrip(v,"{}") for v in variables]
    
    return variables

def get_bash_variables_used_in_path(path):
    with open(path,"r") as f:
        text=f.read()
    return get_bash_variables_used_in_text(text)