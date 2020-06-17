import json
import lxml

from utilities.shell import safe_check_output_with_status, safe_check_output
from constants.path import TMP_FOLDER
from lxml import etree

def pretty(item):
    """
    Returns a string, pretty printing whatever object this is.
    """
    if type(item) is lxml.etree._Element:
        return pretty_xml(item)
    elif type(item) in (dict,list,tuple):
        return pretty_json(item)
    else:
        return str(item)

def pprint(item):
    """
    Pretty print this item. For example, XML, JSON, or whatever else.
    """
    print(pretty(item))

def pretty_kwargs(**kwargs):
    chunks=[]
    longest_key=max([len(key) for key in kwargs])
    chunks.append("*"*40+"\n")
    keys=sorted(list(kwargs.keys()))
    for key in keys:
        value=kwargs[key]
        chunks.append("\n"+key+" "*(longest_key-len(key)+1)+" = ")
        multiline="\n" if "\n" in pretty(value) or type(value) is str else ""
        chunks.append(multiline+pretty(value)+multiline)
    return "".join(chunks)

def pprint_kwargs(**kwargs):
    """
    pretty print all keyword arguments. example:
        
        pprint_kwargs(a="aaa", b="bbb", ...)
        
        a     = aaa
        b     = bbb
    """
    print(pretty_kwargs(**kwargs))
    
pk=pprint_kwargs

def pretty_xml(xml):
    """
    Given an xml string or lxml root, returns a pretty printed XML string.
    
    I'm very surprised and disappointed that lxml pretty_print appears to be garbage. This uses shell xmllint and tmp file instead.
    """
    
    if type(xml) is str:
        tree=etree.fromstring(xml, parser=etree.XMLParser())
    else:
        tree=xml
    
    output,status=safe_check_output_with_status("which xmllint")
    if status!=0:
        raise ValueError("Cannot return pretty xml, missing xmllint.")
    
    tmp_xml=TMP_FOLDER+"tmp_xml"
    with open(tmp_xml,"w") as f:
        f.write(etree.tostring(tree).decode())
    cmd="xmllint --format "+tmp_xml
    output=safe_check_output(cmd)
    
    """remove first line:
        <?xml version="1.0"?>
    """
    return output[output.index("\n")+1:].strip()
    
def pretty_json(j):
    "Return a pretty JSON string."
    return json.dumps(j,indent=4,sort_keys=True,default=lambda o: str(o))
