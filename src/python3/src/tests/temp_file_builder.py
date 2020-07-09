
"""
Some tests require paths to be inserted into files before running. For example,
inserting the absolute mock test folder into an XML, which changes for whoever runs
the tests.

These functions prepare those files.
"""
import shutil
import os
from lxml import etree
from utilities.shell import safe_check_output_with_status
from utilities.xml import xml_cache

from tests.path import MOCK_FILES, TMP_FOLDER

def setup_tmp_smco501_home():
    """
    Returns a path to a 501-like home that:
        does not produce w011
        does produce w012
    """
    
    source=MOCK_FILES+"heimdall/homes/smco501"
    target=TMP_FOLDER+"smco501"
    
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source,target,symlinks=True)
        
    xml_path=target+"/xflow.suites.xml"
    
    root=xml_cache.get(xml_path)
    
    
    exp=MOCK_FILES+"heimdall/suites_without_codes/w011"    
    root.xpath("//Exp")[0].text=exp
    
    exp=MOCK_FILES+"heimdall/suites_with_codes/w012"
    root.xpath("//Exp")[1].text=exp
        
    with open(xml_path,"w") as f:
        data=etree.tostring(root).decode("utf8")
        f.write(data)
        
    return target

def setup_tmp_experiment1():
    """
    Returns a path to an experiment that produces the b001, w015 codes.
    """
    
    source=MOCK_FILES+"heimdall/suites_with_codes/e005"
    target=TMP_FOLDER+"b001"
    
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source,target,symlinks=True)
        
    xml_path=target+"/resources/module1/module2/task1.xml"
    
    root=xml_cache.get(xml_path)
    
    "this is the dynamic value to insert, which changes depending on who runs the test suite where"
    exp=MOCK_FILES+"heimdall/suites_with_codes/w001"
    
    for element in root.xpath("//DEPENDS_ON"):
        element.set("exp",exp)
        
    with open(xml_path,"w") as f:
        data=etree.tostring(root).decode("utf8")
        f.write(data)
        
    "create new git repo so there are uncommited changes for w15"
    cmd="cd %s ; git init ; sleep 0.1"%target
    output,status=safe_check_output_with_status(cmd)
    assert status==0
    
    return target
