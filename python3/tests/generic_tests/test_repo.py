
import unittest
import os.path

from constants import MAESTRO_ROOT, HEIMDALL_CODES_DOC_EN, HEIMDALL_CODES_DOC_FR
from utilities.shell import safe_check_output_with_status
from utilities.path import get_links_source_and_target
from tests.path import ABSOLUTE_SYMLINK_EXISTS_PATH
from heimdall.message_manager import hmm

"""
Test the actual files of the maestro repo.

For example, the project should have no links to absolute paths, since someone
else performing a git clone will have a broken project.
"""


class TestRepo(unittest.TestCase):
    
    def test_codes_documentation(self):
        """
        Every code should be in the automatically generated documentation.
        If not, the generator script should be run.
        """
        
        for path in (HEIMDALL_CODES_DOC_EN,HEIMDALL_CODES_DOC_FR):
            with open(path,"r") as f:
                text=f.read()
            
            missing=[code for code in hmm.codes if code not in text]
            msg="File '%s' is missing the codes %s. The 'generate_messages_markdown.py' should be run to regenerate the documentation."%(path,str(missing))
            self.assertFalse(missing,msg=msg)

    def test_absolute_links(self):
        """
        No symlinks with absolute targets, unless in exception list.
        """

        """
        If target/source starts with this, allow it.
        """
        allowed_targets = ["/does/not/exist",
                           "/dev/null",
                           "/this/does/not/exist",
                           "/this/does/not/exist/and/is/different",
                           "/does-not-exist-but-that-is-okay"]
        allowed_sources = [MAESTRO_ROOT+"mock_files/file_index/modules/main/do-not-follow-this-link",
                           MAESTRO_ROOT+"venv"]

        results = get_links_source_and_target(MAESTRO_ROOT)
        self.assertTrue(results)
        
        ignores=[MAESTRO_ROOT+"python_venv/",
                MAESTRO_ROOT+"src/venv/",
                MAESTRO_ROOT+"build/",
                ABSOLUTE_SYMLINK_EXISTS_PATH]
        def should_ignore(path):
            for ignore in ignores:
                if ignore in path:
                    return True
            return False                

        for d in results:
            
            if should_ignore(d["source"]):
                continue

            if any([a for a in allowed_sources if d["source"].startswith(a)]):
                continue

            if any([a for a in allowed_targets if d["target"].startswith(a)]):
                continue
            
            is_absolute_symlink = d["target"].startswith("/")
            self.assertFalse(is_absolute_symlink, msg=str(d))