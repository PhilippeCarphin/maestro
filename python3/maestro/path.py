import os
import os.path

def get_node_folder_from_node_path(node_path):
    """
    Given a node path like:
        /module1/task1/
        /module1/task1
    Returns:
        /module1
    """
    if node_path.endswith("/"):
        node_path=node_path[:-1]
    return os.path.dirname(node_path)

def resolve_dependency_path(dep_name,node_path):
    """
    Given a dep_name like:
        /module1/task1
        ./task2
        ../task3
    and a node_path:
        /module1/loop1
    Returns the full, resolved node_path:
        /module1/task1
        /module1/loop1/task2
        /module1/task3
    """
    
    if dep_name.startswith("/"):
        return dep_name
    
    node_folder=get_node_folder_from_node_path(node_path)
    
    if not node_folder.startswith("/"):
        node_folder="/"+node_folder
    
    if dep_name.startswith("./"):
        return node_folder+dep_name[1:]
        
    return os.path.normpath(node_folder+"/"+dep_name)


def find_exp_home_in_path(path):
    """
    Travel up the directory tree in path until a valid maestro experiment
    SEQ_EXP_HOME is found, return that.
    """
    cursor = path
    while cursor and cursor != "/":
        path = cursor+"/EntryModule"
        if os.path.isdir(path):
            if not cursor.endswith("/"):
                cursor += "/"
            return cursor
        cursor = os.path.dirname(cursor)
    return ""


def get_exp_home_from_pwd():
    pwd = os.getcwd()
    path = find_exp_home_in_path(pwd)
    if path:
        return path
    return os.path.realpath("")


def get_experiment_name(path):
    """
    Given a path like:
        /suites/gdps/g0
    returns:
        gdps/g0
    """

    if path.endswith("/"):
        path = path[:-1]

    chunks = path.split("/")
    return chunks[-2]+"/"+chunks[-1]
