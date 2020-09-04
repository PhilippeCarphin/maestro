import re
from utilities.generic import superstrip

"""
Matches:
    $ABC
    ${ABC}
"""
BASH_VARIABLE_OPTIONAL_CURLY_REGEX=re.compile("\\$({[\\w]+}|[\\w]+)")

def get_bash_variables_used_in_text(text):
    """
    Given text like:
        echo 123 $ABC ${CAT}
    returns:
        ["ABC","CAT"]
    """
    variables=BASH_VARIABLE_OPTIONAL_CURLY_REGEX.findall(text)
    
    "strip curly brackets"
    variables=[superstrip(v,"{}") for v in variables]
    
    return variables

def get_bash_variables_used_in_path(path):
    with open(path,"r") as f:
        text=f.read()
    return get_bash_variables_used_in_text(text)