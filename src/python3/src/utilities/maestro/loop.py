import os.path
from lxml import etree
from collections import OrderedDict

from utilities import xml_cache
from utilities.maestro.xml import is_element

"""
The functions here read and parse loop XMLs and definitions to build lists of loop indexes.

This involves a few data structures defined here:
    
loop_data:
    {"start":0,
     "end":10,
     "step":1,
     "set":1}

loop_composite_data:
    [loop_data1, loop_data2, ...]

expression:
    "0:10:1:1,40:50:1:1"
found in <LOOP expression="">

loop_index_map:
    OrderedDict
    {"loop1":[0,1,2],
     "loop2":[4,5,6]}

loop_index_selection:
    OrderedDict
    {"loop1":0,
     "loop2":4}

loop_indexes, indexes:
    [integer1, integer2, ...]

"""

def get_loop_indexes_from_expression(expression,logger=None):
    composite=get_loop_composite_data_from_expression(expression,logger=logger)
    indexes=[]
    for loop_data in composite:
        indexes+=get_loop_indexes_from_loop_data(**loop_data)
    return indexes

def get_loop_indexes_from_loop_data(start,end,step,**kwargs):
    """
    Given (1,7,2) returns (1,3,5,7)
    
    (start,end,step) can also be numeric strings.
    """
    try:
        start=int(start)
        end=int(end)
        step=int(step)
    except:
        return []
    
    return list(range(start,end+1,step))        

def get_loop_composite_data_from_xml(xml,logger=None):
    """
    Given a path to an XML or an lxml element returns a loop_composite_data.
    See the top of this file for data descriptions.
    
    A single <LOOP> element in a resource file can have just one of each 
    start/end/step/set attribute, or one loop expression in <LOOP> can contain
    many start/end/step/set values.
    """
    
    "is_element precedes 'not xml' to avoid silly lxml warning about boolean checks on elements"
    if not is_element(xml) and not xml:
        return []
    
    if type(xml) is str:
        root=xml_cache.get(xml)
        if root is None:
            if logger:
                logger.error("Failed to get loop data. Bad xml file '%s'"%xml)
            return []
    elif is_element(xml):
        root=xml
    else:
        if logger:
            logger.error("Failed to get loop data. Not a path to an XML or an lxml element: '%s'"%xml)
        return []
    
    elements=root.xpath("/NODE_RESOURCES/LOOP")
    if not elements:
        if logger:
            logger.error("Failed to get loop data. No <LOOP> in the xml '%s'"%xml)
        return []
    element=elements[0]
    
    expression=element.attrib.get("expression")    
    if expression:
        return get_loop_composite_data_from_expression(expression,logger=logger)
    
    try:
        loop_data={"start":int(element.attrib["start"]),
                   "end":int(element.attrib["end"]),
                   "step":int(element.attrib.get("step",1)),
                   "set":int(element.attrib.get("set",1))}
        return [loop_data]
    except (KeyError, ValueError):
        if logger:
            logger.error("Failed to get loop data. Bad <LOOP> attributes: "+str(element.attrib))
    
    return []        
        
def get_loop_composite_data_from_expression(expression,logger=None):
    """
    Given the expression attribute string in <LOOP>
    returns a loop_composite_data.
    See the top of this file for data descriptions.    
    """
    assert type(expression) is str
    
    chunks=expression.split(",")
    data=[]
    for chunk in chunks:
        numbers=chunk.split(":")
        
        "numbers must be 4 integers"
        for i,number in enumerate(numbers[:]):
            if number.isdigit():
                numbers[i]=int(number)
            else:
                numbers=[]
                break
        if len(numbers)!=4:
            if logger:
                logger.error("skipping bad <LOOP> expression '%s'"%chunk)
            continue
        
        loop_data={"start":int(numbers[0]),
                   "end":int(numbers[1]),
                   "step":int(numbers[2]),
                   "set":int(numbers[3])}
        data.append(loop_data)
    return data
