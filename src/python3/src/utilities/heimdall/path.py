import os.path

def get_ancestor_folders(folder,experiment_path):
    """
    Given a folder:
        /experiment/folder1/folder2
    and experiment_path:
        /experiment
    returns:
        ["/experiment/folder1/folder2",
         "/experiment/folder1",
         "/experiment"]
    """
    folders=set()
    parent=folder
    while parent.startswith(experiment_path):
        if parent!=folder:
            folders.add(parent)
        parent=os.path.dirname(parent)
    return sorted(list(set(folders)))