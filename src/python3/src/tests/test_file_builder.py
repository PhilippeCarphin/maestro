
"""
Some tests require paths to be inserted into files before running. For example,
inserting the absolute mock test folder into an XML, which changes for whoever runs
the tests.

Also, some files are not easily added to git repos, like fake '.git' folders.

These functions prepare those files.
"""
import shutil
import os
from lxml import etree
from utilities.shell import safe_check_output_with_status
from utilities.xml import xml_cache

from tests.path import MOCK_FILES, TMP_FOLDER, TURTLE_ME_PATH, ABSOLUTE_SYMLINK_EXISTS_PATH, OPERATIONAL_HOME

def setup_tricky_mock_files():
    """
    Create files in 'mock_files' not easily added to a git repo, like '.git'
    """
    
    folders=(MOCK_FILES+"suites_with_codes/w018/.git",
             MOCK_FILES+"suites_with_codes/e005/.git")
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)
        empty=folder+"/empty-file"
        with open(empty,"w") as f:
            f.write(" ")
    
    "create a symlink with an absolute path to a file that exists"
    source=ABSOLUTE_SYMLINK_EXISTS_PATH
    target=TURTLE_ME_PATH+"experiment.cfg"
    try:
        os.symlink(target,source)
    except FileExistsError:
        pass

def setup_tmp_git_author_repo(always_recreate=False):
    """
    This git repo is used for the lead developers scan.
    """
    path = TMP_FOLDER+"git-author-repo"
    if not always_recreate and os.path.exists(path):
        return path

    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
    shutil.copytree(TURTLE_ME_PATH, path, symlinks=True)

    author1a = "Jim Jim <jim@jim.org>"
    author1b = "Jim Jim <jimmy@jimmy.org>"
    author1c = "Jimbo Jimbo <jim@jimbo.org>"
    author2 = "Joe Joe <joe@joe.org>"

    commands = ["cd "+path,
                "git init",
                "echo content1 > file1",
                "git add file1",
                "git commit --author=\"%s\" -am \"commit-1\" " % author1a,
                "echo content2 > file1",
                "git commit --author=\"%s\" -am \"commit-2\" " % author1b,
                "echo content3 > file1",
                "git commit --author=\"%s\" -am \"commit-3\" " % author2,
                "echo content4 > file1",
                "git commit --author=\"%s\" -am \"commit-4\" " % author1c]
    cmd = " && ".join(commands)

    output, status = safe_check_output_with_status(cmd)
    if status != 0:
        raise ValueError("status '%s' from cmd '%s' output =\n%s" % (status, cmd, output))

    return path


def setup_tmp_smco501_home():
    """
    Returns a path to a 501-like home that:
        does not produce w011
        does produce w012
    """

    source = MOCK_FILES+"homes/smco501"
    target = TMP_FOLDER+"smco501"

    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True)

    xml_path = target+"/xflow.suites.xml"

    root = xml_cache.get(xml_path)

    exp = MOCK_FILES+"suites_without_codes/w011"
    root.xpath("//Exp")[0].text = exp

    exp = MOCK_FILES+"suites_with_codes/w012"
    root.xpath("//Exp")[1].text = exp

    with open(xml_path, "w") as f:
        data = etree.tostring(root).decode("utf8")
        f.write(data)

    return target


def setup_tmp_experiment1():
    """
    Returns a path to an experiment that produces the b001, w015, i008, w028 codes.
    
    For example, dynamic values will change depending on who runs the test suite and from where.
    """

    source = MOCK_FILES+"suites_with_codes/e005"
    target = TMP_FOLDER+"b001"

    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True)

    xml_path = target+"/resources/module1/module2/task1.xml"
    cfg_path = target+"/resources/module1/task1.cfg"
    resource_path = target+"/resources/resources.def"

    root = xml_cache.get(xml_path)
    
    "depends on a full experiment path that exists"
    exp = MOCK_FILES+"suites_with_codes/w001"
    for element in root.xpath("//DEPENDS_ON"):
        element.set("exp", exp)
    with open(xml_path, "w") as f:
        data = etree.tostring(root).decode("utf8")
        f.write(data)
    
    "ssm use line with old ssm domain"
    line=". ssmuse-sh -d "+MOCK_FILES+"ssm-versions/1.6"
    with open(cfg_path,"a") as f:
        f.write("\n\n"+line)
        
    "add line to resources.def to a full path to an experiment that exists"
    line="PATH_TO_NOT_DATESTAMPED_SUITE="+MOCK_FILES+"suites_with_codes/w001"
    with open(resource_path,"a") as f:
        f.write("\n\n"+line)
        
    "add an absolute path to an operational file"
    line="ABSOLUTE_PATH_TO_OP_USER="+OPERATIONAL_HOME+"smco500/maestro_suites/zdps/modules/module1/task1.tsk"
    with open(cfg_path,"a") as f:
        f.write("\n\n"+line)
        
    "create new git repo so there are uncommited changes for w15"
    cmd = "cd %s ; git init ; sleep 0.1" % target
    output, status = safe_check_output_with_status(cmd)
    assert status == 0
    
    "change origin remote to not GitLab for b025"
    cmd = "cd %s ; git remote add origin /home/abc123/not/gitlab ; sleep 0.1" % target
    output, status = safe_check_output_with_status(cmd)
    assert status == 0
    
    "permissions"
    cmd = "cd %s ; chmod 700 modules/module1/task1.cfg" % target
    output, status = safe_check_output_with_status(cmd)
    assert status == 0
    cmd = "cd %s ; chmod 700 listings" % target
    output, status = safe_check_output_with_status(cmd)
    assert status == 0

    return target


def setup_tmp_experiment2():
    """
    Returns a path to an experiment that produces the i007 code.
    """

    source = MOCK_FILES+"suites_with_codes/b007"
    target = TMP_FOLDER+"i007"

    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True)

    cfg_path = target+"/modules/module1/task1.cfg"
        
    "add an absolute path to an operational file"
    line="ABSOLUTE_PATH_TO_OP_USER="+OPERATIONAL_HOME+"smco500/maestro_suites/zdps/modules/module1/task1.tsk"
    with open(cfg_path,"a") as f:
        f.write("\n\n"+line)

    return target