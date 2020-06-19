
"""
FileCache caches information about files like their contents or file stats.
This way, Heimdall can requery files whenever it needs to without performance
concerns.

Instead of 'os.path' or 'os.listdir' Heimdall should use these 
same-name functions instead.
"""

import os
import os.path
from lxml import etree

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
    """
    Some functions do not have cache, for example when
    they cache key should be realpath and not path.
    This prevents caching duplicates for two paths that have the same realpath.
    """
    
    def __init__(self):
        self.xml_parser=etree.XMLParser()
    
    def etree_parse(self,path):
        """
        Return the parsed lxml element for the XML at this path.
        Error returns None.
        """
        realpath=self.realpath(path)   
        return self.etree_parse_from_realpath(realpath)
    
    @cache
    def etree_parse_from_realpath(self,realpath):
        try:
            tree=etree.parse(realpath, parser=self.xml_parser)
            return tree.getroot()
        except:
            return None
    
    def open(self,path):
        realpath=self.realpath(path)
        return self.open_realpath(realpath)
    
    @cache
    def open_realpath(self,realpath):
        if self.isfile(realpath):
            with open(realpath,"r") as f:
                return f.read()
        return ""
    
    @cache
    def is_broken_symlink(self,path):
        return self.islink(path) and not os.path.exists(self.readlink(path))
    
    @cache
    def readlink(self,path):
        return os.readlink(path)
    
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