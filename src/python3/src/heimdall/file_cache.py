
"""
FileCache caches information about files like their contents or file stats.
This way, Heimdall can requery files whenever it needs to without performance
concerns.

Instead of 'os.path' or 'os.listdir' Heimdall should use these 
same-name functions instead.
"""

import os
import os.path

def cache(function):
    """
    later versions of Python have 'functools.cache'
    """
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper

class FileCache():
    def __init__(self):
        pass
        
    def open(self,path):
        """
        this function does not use cache decorator, because
        the cache key is realpath, not path
        """
        realpath=self.realpath(path)
        return self.open_realpath(realpath)
    
    @cache
    def open_realpath(self,realpath):
        if self.isfile(realpath):
            with open(realpath,"r") as f:
                return f.read()
        return ""
    
    @cache
    def listdir(self,path):
        return os.listdir(path)
    
    @cache
    def isfile(self,path):
        return os.path.isfile(path)
    
    @cache
    def isdir(self,path):
        return os.path.isdir(path)
    
    @cache
    def islink(self,path):
        return os.path.islink(path)
    
    @cache
    def exists(self,path):
        return os.path.exists(path)
    
    @cache
    def realpath(self,path):
        return os.path.realpath(path)
    
file_cache=FileCache()