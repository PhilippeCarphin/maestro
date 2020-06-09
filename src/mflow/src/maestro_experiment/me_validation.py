
"""
This code handles validation code, like validating maestro experiment files, or the user environment.

This abstract class is not meant to be instantiated, only inherited.
"""

import os

from maestro.sequencer import environment_has_maestro

class ME_Validation():

    def is_valid(self):
        """
        Returns true if this experiment parsed properly and seems to be valid.
        """
        return len(self.validation_errors)==0
    
    def can_user_send_maestro_signals(self):
        """
        Returns true if the folders and write permissions in this experiment allow 
        running a maestro command, like submitting a node.
        """
        
        return not self.explain_cannot_send_maestro_signals()
    
    def explain_cannot_send_maestro_signals(self):
        """
        If the folders and write permissions in this experiment do not allow 
        running a maestro command, like submitting a node, then
        return a list of string messages explaining why not.
        """
        
        messages=[]
        folders=["listings","logs","sequencing","hub"]
        user=os.environ.get("USER","")
        for folder in folders:
            path=self.path+folder
            if not os.path.exists(path):
                messages.append("Required folder does not exist: '%s'"%folder)
                continue
            if not os.access(path,os.W_OK):
                messages.append("User '%s' needs write permission on folder: '%s'"%(user,folder))
                continue
        
        path=self.path+"EntryModule"
        if not os.path.exists(path):
            messages.append("Required folder/link does not exist: '%s'"%path)
        
        if not environment_has_maestro():
            messages.append("No 'maestro' command found in your environment. You may be missing an 'ssmuse-sh' command. See the 'maestro' quick start guide for more information.")
        
        return messages
    