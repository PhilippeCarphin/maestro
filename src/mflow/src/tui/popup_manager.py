import os.path
import functools
import datetime
import time
import copy

from tui.text_flow import TextFlow
from tui.utilities import pad_text_with_spaces
from constants import TUI_STATE, TMP_FOLDER
from utilities import safe_check_output, safe_check_output_with_status, \
run_shell_cmd, is_gzipped, safe_write, pretty
from mflow_utilities import logger
from maestro.sequencer import get_sequencer_loop_argument, get_sequencer_command

"""
This class handles all popups.
It extends TuiManager and is not meant to be instantiated by itself.
"""

class PopupManager:
    
    def confirm_selected_popup_choice(self):
        "whichever popup choice is selected now, run its confirmation function, clear the popup."
        choices=self.choice_popup["choices"]
        index=self.choice_popup["selected_index"]
        choice=choices[index]
        function=choice.get("function")
            
        self.set_tui_state(TUI_STATE.FLOW_NAVIGATE)
        
        if callable(function):
            function()
    
    def popup_select_node(self,node_path):
        "called when this node has been selected, show popup with options"        
        
        self.choices_popup_overflow_index=0
        leaf=node_path.split("/")[-1]
        text="Node '%s'"%leaf
        
        choices=self.get_popup_choices_for_node(node_path)
        
        self.choice_popup={"text":text,
                           "selected_index":0,
                           "choices": choices}
        
        self.set_tui_state(TUI_STATE.CHOICE_POPUP)
    
    def popup_okay_message(self,message):
        """
        show a simple popup where you must simply press enter for okay
        the message can be long, it is automatically split into separate lines as necessary.
        """
        
        self.choices_popup_overflow_index=0
        choice={"label":"Okay",
                "function": None}
        self.choice_popup={"text":message,
                           "selected_index":0,
                           "choices": [choice],
                           "top_border_text":"",
                           "bottom_border_text":"",
                           "center_choice_text":True}
        
        self.set_tui_state(TUI_STATE.CHOICE_POPUP)
        
    def popup_choice_functions(self,text,
                               choice_labels,
                               choice_functions,
                               top_border_text=""):
        """
        Show a popup with these choices.
        Run the choice_function of the matching choice_label if it is selected.
        """
        assert len(choice_labels) == len(choice_functions)
        assert choice_labels
        
        self.choices_popup_overflow_index=0
        choices=[]
        for i in range(len(choice_labels)):
            choices.append({"label":choice_labels[i],
                            "function": choice_functions[i]})
            
        self.choice_popup={"text":text,
                           "selected_index":0,
                           "choices": choices,
                           "top_border_text":top_border_text,
                           "bottom_border_text":"",
                           "center_choice_text":True}
        
        self.set_tui_state(TUI_STATE.CHOICE_POPUP)
        
    def popup_select_node_index(self,node_path):
        "called when the user wants to choose a loop index for this node."        
        
        self.choices_popup_overflow_index=0
        leaf=node_path.split("/")[-1]
        node_data=self.maestro_experiment.get_node_data(node_path)
        indexes=node_data["loop_indexes_available"]
        
        choices=[]
        for index in indexes:
            choice={"label":"index = %s"%index,
                    "function": functools.partial(self.text_flow.set_node_selected_loop_index,
                                                  node_path,
                                                  index)}
            choices.append(choice)
        
        selected_now=self.text_flow.get_selected_index_for_node(node_path)
        
        if selected_now in indexes:
            selected_now=indexes.index(selected_now)
        else:
            selected_now=0
        
        self.choice_popup={"text":"Select a loop index for '%s'"%leaf,
                           "selected_index":selected_now,
                           "choices": choices}
        
        self.set_tui_state(TUI_STATE.CHOICE_POPUP)
        
    def get_popup_choices_for_node(self,node_path):
        
        choices=[]
        node_data=self.maestro_experiment.get_node_data(node_path)
        me=self.maestro_experiment
        
        "collapse/uncollapse"
        if me.has_children(node_path):
            if self.is_node_collapsed(node_path):
                choice={"label":"Expand Children (uncollapse)",
                        "function": functools.partial(TextFlow.set_node_collapsed,self.text_flow,node_path,False,tui_manager=self)}
            else:
                choice={"label":"Collapse Children",
                        "function": functools.partial(TextFlow.set_node_collapsed,self.text_flow,node_path,True,tui_manager=self)}
            choices.append(choice)
        
        "select loop index"
        if self.maestro_experiment.has_indexes(node_path):
            choice={"label":"Select Loop Index",
                    "function": functools.partial(self.popup_select_node_index,node_path)}
            choices.append(choice)        
            
        "only show options to open text files if the way this script was launched allows it"
        if self.can_schedule_commands():
            "nodeinfo"
            cmd="nodeinfo -e %s -n %s"%(me.path,node_path)
            choice={"label":"Node Info",
                    "function": self.get_function_to_view_command_output(cmd)}
            choices.append(choice)
            
            "logs"
            log_types=("success","submission","abort")
            for log_type in log_types:
                log_path=me.get_latest_log(node_path,log_type)
                is_file=log_path and os.path.isfile(log_path)
                if is_file:
                    choice={"label":"Logs: show latest %s"%log_type,
                            "function": self.get_function_to_view_file(log_path)}
                    choices.append(choice)
            
            "maestro repo files"
            prefixes={"config":"configuration CFG",
                      "flow":"flow XML",
                      "resource":"resources XML",
                      "task":"task TSK"}
            open_tmp_copy=not self.is_edit_mode
            create_if_empty=self.is_edit_mode
            for prefix,label in prefixes.items():
                key=prefix+"_path"
                path=node_data.get(key,"")
                is_file=path and os.path.isfile(path)
                if not is_file:
                    logger.debug("Not a file: '%s'"%path)
                if is_file or self.is_edit_mode:
                    verb="view" if open_tmp_copy else "edit"
                    button_label="File: %s %s"%(verb,label)
                    if not is_file:
                        button_label+=" (empty)"
                        
                    f=self.get_function_to_view_file(path,
                                                     open_tmp_copy=open_tmp_copy,
                                                     create_if_empty=create_if_empty)
                    choice={"label":button_label,
                            "function": f}
                    choices.append(choice)
        
        "view work directory"
        workdir=me.get_workdir_path(node_path)
        if os.path.isdir(workdir) or self.is_debug:
            cmd=self.tui_config["VIEW_WORKDIR_COMMAND"]%workdir
            f=self.get_function_to_confirm_cmd(cmd,show_command_output=False)
            choice={"label":"Workdir: Open New Terminal Window",
                    "function": f}
            choices.append(choice)
        
        if self.is_debug:
            choice={"label":"Debug: run 'ls'",
                    "function":self.get_function_to_confirm_cmd("ls")}
            choices.append(choice)
        
        if me.can_user_send_maestro_signals(node_data=node_data) or self.is_debug:
            choices+=self.get_sequencer_choices(node_path)
        else:
            choice={"label":"Submit (disabled). Explain why.",
                    "function":self.popup_explain_disabled_submit}
            choices.append(choice)
        
        return choices        
    
    def get_sequencer_choices(self,node_path):
        """
        Returns a list of popup menu choices for 'maestro' commands like
        submit & continue, force status, etc.
        """
        
        choices=[]
        me=self.maestro_experiment
        lis=self.text_flow.get_loop_index_selection(node_path)
        has_indexes=me.has_indexes(node_path)
        last_index=None
        if lis:
            last_index=next(reversed(lis.values()))
        
        """
        lis_leafless is loop_index_selection with the last element removed.
        This is used in cases where we want to submit all loop members of the current leaf,
        which is done by not specifying the loop index for this leaf, only its parents.
        """
        lis_leafless=copy.copy(lis)
        if lis_leafless:
            "next-reversed finds the last key in OrderedDict"
            lis_leafless.pop(next(reversed(lis_leafless)))
        
        label="Submit: continue"
        indexes=lis
        if has_indexes:
            label+=", entire loop"
            indexes=lis_leafless
        choice={"label":label,
                "cmd":me.get_sequencer_command(node_path,"submit",
                                                loop_index_selection=indexes)}
        choices.append(choice)
        
        if not has_indexes:
            label="Submit: stop"
            choice={"label":label,
                    "cmd":me.get_sequencer_command(node_path,"submit",
                                                    loop_index_selection=lis,
                                                    is_continue=False)}
            choices.append(choice)
        
        if has_indexes:
            label="Submit: continue, loop member (%s)"%last_index
            choice={"label":label,
                    "cmd":me.get_sequencer_command(node_path,"submit",
                                                    loop_index_selection=lis)}
            choices.append(choice)
        
        label="Submit: continue, no dependency"
        indexes=lis
        if has_indexes:
            label+=", entire loop"
            indexes=lis_leafless
        choice={"label":label,
                "cmd":me.get_sequencer_command(node_path,"submit",
                                                loop_index_selection=indexes,
                                                is_no_dependency=True)}
        choices.append(choice)
        
        if not has_indexes:
            label="Submit: stop, no dependency"
            choice={"label":label,
                    "cmd":me.get_sequencer_command(node_path,"submit",
                                                    loop_index_selection=lis,
                                                    is_continue=False,
                                                    is_no_dependency=True)}
            choices.append(choice)
        
        if has_indexes:
            label="Submit: continue, no dependency, loop member (%s)"%last_index
            choice={"label":label,
                    "cmd":me.get_sequencer_command(node_path,"submit",
                                                    loop_index_selection=lis,
                                                    is_no_dependency=True)}
            choices.append(choice)   
        
        """
        force status signals
        Unfortunately, this section is either hard to read, or has lots of copied lines of code.
        I went with hard to read.
        """
        signals=("initnode","begin","end","abort")
        for target in ("","member","loop"):
            for signal in signals:
                if target and not has_indexes:
                    continue
                                            
                if has_indexes and not target:
                    continue
                
                inner=""
                if target=="member":
                    inner="loop member (%s) "%last_index
                if target=="loop":
                    inner="entire loop "
                
                label="Force status: %s%s"%(inner,signal)
                indexes=lis if target!="loop" else lis_leafless                    
                cmd=me.get_sequencer_command(node_path,signal,
                                              loop_index_selection=indexes,
                                              is_continue=False)
                choices.append({"label":label,"cmd":cmd})
        
        "assign function in this loop to avoid tremendous duplication above"
        for choice in choices:
            if "function" not in choice:
                show_command_output=self.tui_config.get("VIEW_MAESTRO_COMMAND_OUTPUT")
                choice["function"]=self.get_function_to_confirm_cmd(choice["cmd"],
                      show_command_output=show_command_output)
        
        return choices
    
    def get_function_to_confirm_cmd(self,cmd,show_command_output=True):
        """
        Returns a function that can be called, to open a popup to 
        confirm running this command.
        """
        return functools.partial(PopupManager.popup_confirm_command_okay,self,cmd,show_command_output)
    
    def popup_confirm_command_okay(self,cmd,show_command_output=True):
        """
        Shows a confirmation popup.
        If user selects yes, runs 'cmd' and optionally show output.
        """
        
        top_border_text="Press enter to run this command. Or 'c' to cancel."
        
        if show_command_output:
            yes=self.get_function_to_view_command_output(cmd)
        else:
            yes=functools.partial(safe_check_output,cmd)
        
        button_width=16
        choice_labels=[pad_text_with_spaces("Run Command",button_width),
                       pad_text_with_spaces("Cancel",button_width)]
        choice_functions=[yes,None]
        
        self.popup_choice_functions(cmd,
                               choice_labels,
                               choice_functions,
                               top_border_text=top_border_text)
    
    def popup_explain_disabled_submit(self):
        messages=self.maestro_experiment.explain_cannot_send_maestro_signals()
        if messages:
            message="The 'maestro' command isn't going to work.\n * "+"\n * ".join(messages)
        else:
            "this should never happen, there should always be some message."
            message="The 'maestro' command isn't going to work, perhaps because of missing folders or permissions."
        self.popup_okay_message(message)
    
    def get_tmp_text_file_path(self):
        return TMP_FOLDER+"temporary_text_file_"+str(time.time())
    
    def get_function_to_view_command_output(self,cmd):
        """
        Returns a callable function that will run this command in a shell, 
        copy its output to a temporary file, and open it with a text viewer.
        """
        
        def view_cmd(popup_manager,cmd):
            logger.debug("get_function_to_view_command_output cmd = "+cmd)
            output,status=safe_check_output_with_status(cmd)
            datestamp=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            text="""# This file shows the output of this command:\n#    %s\n# run on %s\n# exit status = %s\n\n"""%(cmd,datestamp,status)
            text+=output
            tmp_file=self.get_tmp_text_file_path()
            with open(tmp_file,"w") as f:
                f.write(text)
            popup_manager.get_function_to_view_file(tmp_file,open_tmp_copy=False)()
            
        return functools.partial(view_cmd,self,cmd)
    
    def get_function_to_view_file(self,path,open_tmp_copy=True,create_if_empty=False):
        """
        Returns a callable function that will open this text file in a new window.
        open_tmp_copy can be used to open a temporary copy, for example to
        prevent accidental editing of log files.
        """
        
        def view_text(path,open_tmp_copy,create_if_empty):
            if create_if_empty and not os.path.isfile(path):
                safe_check_output("mkdir -p $(dirname %s)"%path)
                safe_check_output("touch "+path)
            
            if not os.path.isfile(path):
                self.add_message("Text file does not exist: '%s'"%path)
                return
            
            use_zcat=is_gzipped(path) and not create_if_empty
            if use_zcat or open_tmp_copy:             
                tmp_file=self.get_tmp_text_file_path()
                tmp_header="""# This file is a temporary copy generated by mflow for viewing in a text editor. The original is found here:\n# %s\n\n"""
                tmp_header=tmp_header%path
                cmd="zcat" if use_zcat else "cat"
                
                safe_write(tmp_file,tmp_header)                
                safe_check_output(cmd+" %s >> %s"%(path,tmp_file))
                path=tmp_file
            
            if not os.path.isfile(path):
                self.add_message("Failed to create temporary text file for viewing: '%s'"%path)
                return
            
            program=self.tui_config["TEXT_VIEWER_AND_EDITOR"]
            
            output,status=safe_check_output_with_status("which "+program)
            if status!=0:
                self.add_message("Bad text viewer program: '%s'"%program)
                return
            
            cmd=program+" "+path
            self.schedule_command_outside_curses(cmd)
        
        return functools.partial(view_text,path,open_tmp_copy,create_if_empty)
            
