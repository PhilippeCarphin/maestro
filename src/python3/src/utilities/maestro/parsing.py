from utilities import superstrip
import re

"""
These match:
    # <input type="  ...   >
and:
    # </output>
where group(1) is the section like 'input'
"""    
SECTION_START_REGEX=re.compile(r"[ ]*#[ ]+<([a-zA-Z]+)[^>]*>")
SECTION_END_REGEX=re.compile(r"[ ]*#[ ]+<\/([a-zA-Z]+)[^>]*>")

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
    
    split_regex=re.compile("[# \t]+")
    section=""
    sections=["input","executables","output"]
    data={a:{} for a in sections}
    for line in text.split("\n"):
        
        if not superstrip(line,"# "):
            continue
        
        if line.strip().startswith("##"):
            continue
        
        if section:
            match=SECTION_END_REGEX.search(line)
            if match:
                section=""
                
        else:
            match=SECTION_START_REGEX.search(line)
            
            if match:
                section=match.group(1)
                if section not in sections:
                    section=""
        
        split=split_regex.split(line)
        
        if section and len(split)==3:
            empty,key,value=split
            if key and value:
                data[section][key]=value
            
    return data
            