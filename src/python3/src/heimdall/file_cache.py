
"""
FileCache caches information about files like their contents or file stats.
This way, Heimdall can requery files whenever it needs to without performance
concerns.

Instead of 'os.path' or 'os.listdir' Heimdall should use these 
same-name functions instead.
"""

import os
import os.path
import hashlib
from pwd import getpwuid, getpwnam
from grp import getgrgid, getgrall
from lxml import etree

from constants import ENCODINGS
from utilities.generic import cache, safe_open, strip_comments_from_text, get_key_values_from_path
from utilities.path import get_link_chain_from_link

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
    def get_link_chain_from_link(self, path):
        return get_link_chain_from_link(path)
        
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
        owner=getpwuid(os_stat.st_uid).pw_name
        group=getgrgid(os_stat.st_gid).gr_name
        
        "convert '0o100644' to '100644'  "
        long_permissions=oct(os_stat.st_mode)[2:]
        
        permissions=long_permissions[-3:]
        return (owner,group,permissions,long_permissions)
    
    def get_ugp_string(self,path):
        """
        Returns a string like:
            zulban:zulban:755
        for the user, group, and permissions of this file.
        """
        name,group,permissions,long_permissions=file_cache.get_user_group_permissions(path)
        if not name or not group or not permissions or not long_permissions:
            return ""
        return "%s:%s:%s"%(name,group,permissions)
    
    def can_user_write_to_path(self,user,path):
        realpath = self.realpath(path)
        return self.can_user_write_to_realpath(user,realpath)
    
    @cache
    def can_user_write_to_realpath(self,user,realpath):
        """
        This function is not written exceptionally well, but at least it uses
        existing caching instead of heavy system IO calls.
        """
        
        owner,group,permissions,_=self.get_user_group_permissions_from_realpath(realpath)
        
        if not owner or not group or not permissions:
            return False
        
        assert len(permissions)==3
        
        write_digits="2367"
        
        if user==owner:
            return permissions[0] in write_digits
        
        try:
            user_group_id = getpwnam(user).pw_gid
            user_group=getgrgid(user_group_id).gr_name
            if user_group == group:
                return permissions[1] in write_digits
        except KeyError:
            pass

        return permissions[2] in write_digits
    
    @cache
    def md5_from_realpath(self,realpath,empty_file_is_empty_string=True,strip_whitespace=True):
        content=self.open_realpath(realpath)
        if strip_whitespace:
            content=content.strip()
        if empty_file_is_empty_string and not content:
            return ""
        encoding="iso-8859-1"
        md5=hashlib.md5(content.encode(encoding)).hexdigest()
        return md5
    
    def md5(self,path,empty_file_is_empty_string=True,strip_whitespace=True):
        realpath = self.realpath(path)
        return self.md5_from_realpath(realpath,
                                      empty_file_is_empty_string=True,
                                      strip_whitespace=True)

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

        link = os.path.join(os.path.dirname(path),os.readlink(path))
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
