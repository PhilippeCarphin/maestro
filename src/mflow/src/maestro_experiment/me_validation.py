
"""
This code handles validation code, like validating maestro experiment files, or the user environment.

This abstract class is not meant to be instantiated, only inherited.
"""

import os

from utilities import logger
from maestro.sequencer import environment_has_maestro

class ME_Validation():
    
    def basic_experiment_validation(self):
        """
        Returns true if this experiment might be valid, before 
        examining the content of any files.
        Adds validation error messages if they pop up.
        """
        
        entry_module_error=self.explain_entry_module_error()

        if not self.path:
            self.add_validation_error("Could not find an experiment for path:\n   %s\nA valid experiment folder contains an 'EntryModule' link file or folder."%path)        
        elif not os.path.exists(self.path):
            self.add_validation_error("Experiment path does not exist: '%s'"%path)
        elif not os.path.isdir(self.path):
            self.add_validation_error("Experiment path is not a folder: '%s'"%path)
        elif entry_module_error:
            self.add_validation_error(entry_module_error)
        
        return self.is_valid()
    
    def add_validation_error(self,message):
        logger.error(message)
        self.validation_errors.append(message)

    def is_valid(self):
        """
        Returns true if all verification checks so far have not found errors.
        """
        return len(self.validation_errors)==0
    
    def has_entry_module_error(self):
        return bool(self.explain_entry_module_error())
    
    def explain_entry_module_error(self):
        """
        If EntryModule is not valid, returns a message explaining why.
        If valid, returns empty.
        """
                
        entry_module_link=self.path+"EntryModule"
        
        if not os.path.exists(entry_module_link):
            return "EntryModule does not exist: '%s'"%entry_module_link
        
        if not os.path.islink(entry_module_link):
            return "EntryModule is not a link: '%s'"%entry_module_link
        
        return ""
    
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
    