
"""
FileInfo cache's info about one file which reduces filesystem and parsing load.
It builds content indexes, cache's filestat results, etc.
"""
class FileInfo():
    def __init__(self,path):
        self.path=path