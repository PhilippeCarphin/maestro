from utilities import superstrip, safe_open
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

"""
Matches lines like:
    ## residus.123 ${SEQ_BIN}/residus.123
found in the pseudo-xml sections of cfg files.
"""
PSEUDO_CONFIG_COMMENTED_LINE=re.compile(r"##[ \t]+[a-zA-Z0-9-_.]+[ \t]+[a-zA-Z0-9-_.]+")
                             
def get_commented_pseudo_xml_lines(content):
    """
    Given text content from a cfg file, returns a list of lines like:
        ## rpy.nml_get        rpy.nml_get
    within the pseudo-xml sections.
    """
    
    lines=[]
    is_pseudo_section=False
    for line in content.split("\n"):
        
        if is_pseudo_section:
            
            if PSEUDO_CONFIG_COMMENTED_LINE.match(line):
                lines.append(line)
            
            if SECTION_END_REGEX.match(line):
                is_pseudo_section=False
        else:
            if SECTION_START_REGEX.match(line):
                is_pseudo_section=True
    
    return lines
                             
def get_weird_assignments_from_config_path(path):
    content=safe_open(path)
    return get_weird_assignments_from_config_text(content)

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
            