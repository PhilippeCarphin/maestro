from utilities import superstrip
import re

def get_weird_assignments_from_config_path(path):
    with open(path,"r") as f:
        return get_weird_assignments_from_config_text(f.read())

def get_weird_assignments_from_config_text(text):
    """
    Parses the weird hash/semi-xml format in some maestro cfg files.
    
    Given some text like this:
        
# <output>
#    anlalt_nosfc     ${ASSIMCYCLE_getalt_output}/${ASSIMCYCLE_DATE}_000_nosfc
# </output>
    
    returns a dictionary:
        {"output":{"anlalt_nosfc":"${ASSIMCYC ..."}}}
    """
    
    data={}
    spaces_regex=re.compile("[ ]+")
    section=""
    sections=["input","executables","output"]
    for line in text.split("\n"):
        a=superstrip(line,"# ")
        if not a:
            continue
        
        if a.startswith("<") and a.endswith(">"):
            if a.startswith("</"):
                section=""
            else:
                section=a[1:-1]
                if section not in sections:
                    continue
                data[section]={}
        else:
            c=spaces_regex.split(a)
            if len(c)==2:
                key,value=c
                data[section][key]=value
    return data
            