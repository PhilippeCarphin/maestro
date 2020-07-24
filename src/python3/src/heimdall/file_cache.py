
"""
FileCache caches information about files like their contents or file stats.
This way, Heimdall can requery files whenever it needs to without performance
concerns.

Instead of 'os.path' or 'os.listdir' Heimdall should use these 
same-name functions instead.
"""

import os
import os.path
from pwd import getpwuid
from grp import getgrgid
from lxml import etree

from constants import ENCODINGS
from utilities.generic import cache, safe_open, strip_comments_from_text, get_key_values_from_path


class FileCache():
    """
    Some functions do not have cache, for example when
    the cache key should be realpath and not path.
    This prevents caching duplicates for two paths that have the same realpath.
    """

    def __init__(self):
        self.xml_parser = etree.XMLParser()

    def etree_parse(self, path):
        """
        Return the parsed lxml element for the XML at this path.
        Error returns None.
        """
        realpath = self.realpath(path)
        return self.etree_parse_from_realpath(realpath)

    @cache
    def get_key_values_from_realpath(self, realpath):
        return get_key_values_from_path(realpath)

    def get_key_values_from_path(self, path):
        realpath = self.realpath(path)
        return self.get_key_values_from_realpath(realpath)

    @cache
    def etree_parse_from_realpath(self, realpath):
        try:
            tree = etree.parse(realpath, parser=self.xml_parser)
            return tree.getroot()
        except:
            return None
    
    def os_stat(self,path):
        realpath = self.realpath(path)
        return self.os_stat_from_realpath(realpath)
    
    @cache
    def os_stat_from_realpath(self, realpath):
        return os.stat(realpath)
    
    def get_user_group_permissions(self,path):
        """
        Return a tuple like:
            ("zulban", "zulban", "644", "100644")
        for user, group, rwx, complete rwx
        """
        realpath = self.realpath(path)
        return self.get_user_group_permissions_from_realpath(realpath)
    
    @cache
    def get_user_group_permissions_from_realpath(self,realpath):
        if not self.exists(realpath):
            return "","","",""
        os_stat=os.stat(realpath)
        name=getpwuid(os_stat.st_uid).pw_name
        group=getgrgid(os_stat.st_gid).gr_name
        
        "convert '0o100644' to '100644'  "
        long_permissions=oct(os_stat.st_mode)[2:]
        
        permissions=long_permissions[-3:]
        return (name,group,permissions,long_permissions)

    @cache
    def open_without_comments(self, path):
        """
        Return the text content of this file, minus any lines that are
        comments, like '#' in bash.
        """
        return strip_comments_from_text(self.open(path))

    def open(self, path):
        realpath = self.realpath(path)
        return self.open_realpath(realpath)

    @cache
    def open_realpath(self, realpath):
        return safe_open(realpath)

    @cache
    def is_broken_symlink(self, path):
        if not self.islink(path):
            return False

        link = os.path.dirname(path)+"/"+os.readlink(path)
        return not self.exists(link)

    @cache
    def readlink(self, path):
        return os.readlink(path)

    @cache
    def listdir(self, path):
        if self.isdir(path):
            return os.listdir(path)
        return []

    @cache
    def isfile(self, path):
        return os.path.isfile(path)

    @cache
    def isdir(self, path):
        return os.path.isdir(path)

    @cache
    def islink(self, path):
        return os.path.islink(path)

    @cache
    def exists(self, path):
        return os.path.exists(path)

    @cache
    def realpath(self, path):
        return os.path.realpath(path)


file_cache = FileCache()
