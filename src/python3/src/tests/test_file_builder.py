
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

from tests.path import MOCK_FILES, TMP_FOLDER, TURTLE_ME_PATH, ABSOLUTE_SYMLINK_EXISTS_PATH

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
    Returns a path to an experiment that produces the b001, w015 codes.
    """

    source = MOCK_FILES+"suites_with_codes/e005"
    target = TMP_FOLDER+"b001"

    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True)

    xml_path = target+"/resources/module1/module2/task1.xml"

    root = xml_cache.get(xml_path)

    "this is the dynamic value to insert, which changes depending on who runs the test suite where"
    exp = MOCK_FILES+"suites_with_codes/w001"

    for element in root.xpath("//DEPENDS_ON"):
        element.set("exp", exp)

    with open(xml_path, "w") as f:
        data = etree.tostring(root).decode("utf8")
        f.write(data)

    "create new git repo so there are uncommited changes for w15"
    cmd = "cd %s ; git init ; sleep 0.1" % target
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
