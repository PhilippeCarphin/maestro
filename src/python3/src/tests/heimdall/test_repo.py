
import unittest
import os.path

from constants import MAESTRO_ROOT
from utilities.shell import safe_check_output_with_status
from utilities.path import get_links_source_and_target

"""
Test the actual files of the maestro repo.

For example, the project should have no links to absolute paths, since someone
else performing a git clone will have a broken project.
"""

class TestRepo(unittest.TestCase):
            
    def test_absolute_links(self):
        """
        No symlinks with absolute targets, unless in exception list.
        """
        
        """
        If target/source starts with this, allow it.
        """
        allowed_targets=["/does/not/exist",
                         "/dev/null",
                         "/this/does/not/exist",
                         "/this/does/not/exist/and/is/different"]
        allowed_sources=[MAESTRO_ROOT+"src/python3/mock_files/heimdall/file_index/modules/main/do-not-follow-this-link",
                         MAESTRO_ROOT+"venv"]
        
        results=get_links_source_and_target(MAESTRO_ROOT)
        self.assertTrue(results)
        
        for d in results:
            
            if any([a for a in allowed_sources if d["source"].startswith(a)]):
                continue
            
            if any([a for a in allowed_targets if d["target"].startswith(a)]):
                continue
            
            is_absolute_symlink=d["target"].startswith("/")
            self.assertFalse(is_absolute_symlink,msg=str(d))
                