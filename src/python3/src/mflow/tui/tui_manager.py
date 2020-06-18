import curses
import json
import time
import os
import os.path
import logging
from curses import wrapper

from maestro.experiment import MaestroExperiment
from utilities.curses import get_curses_attr_from_string
from utilities import clamp, get_console_dimensions, pretty, safe_write, run_shell_cmd
from mflow.utilities import logger, set_log_level, get_mflow_config
from constants import NAVIGATION_KEYS, TUI_STATE, VERSION, KEYBOARD_NAVIGATION_TYPE, TMP_BASH_WRAPPER_COMMAND_FILE_PREFIX, MINIMUM_CONSOLE_DIMENSIONS, TMP_FOLDER, LOG_FOLDER
from mflow.tui.text_flow import TextFlow
from mflow.tui import PopupManager
from mflow.tui.utilities import get_text_lines_within_width, pad_text_with_spaces

CURSOR_POINTS=((-1,0),(0,1),(1,0),(0,-1))

class TuiManager(PopupManager):
    def __init__(self,
                 maestro_experiment,
                 tui_config=None,
                 cursor_start_xy=(1,1),
                 is_debug=False,
                 debug_keypresses=None,
                 debug_q_after_keypresses=True,
                 debug_okay_messages=None,
                 debug_keypress_sleep=0,
                 verbose=False,
                 tui_id=None):
        
        assert type(maestro_experiment) is MaestroExperiment
        self.maestro_experiment=maestro_experiment
        self.last_experiment_refresh_time=time.time()
        self.cursor_start_xy=cursor_start_xy
        self.is_edit_mode=False
        self.verbose=verbose
        self.is_debug=is_debug
        
        self.cleanup_old_tui_files()
        
        if not tui_id:
            tui_id=str(time.time)
        self.tui_id=tui_id
        self.tui_restore_data_path=TMP_FOLDER+".tui-restore-data-%s.json"%self.tui_id
        
        if verbose:
            set_log_level(logging.DEBUG)
        
        """
        This is an optional list of character integers to simulate user keypresses for tests.
        End with a "q" quit by default, for easier test case writing.
        """
        if not debug_keypresses:
            debug_keypresses=[]
        if debug_q_after_keypresses and debug_keypresses:
            debug_keypresses.append(ord("q"))
        self.debug_keypresses=debug_keypresses
        self.allow_user_input=not bool(debug_keypresses)
        
        """
        Wait this many seconds between debug key presses.
        Useful to see the automated tui interaction in tests.
        """
        self.debug_keypress_sleep=debug_keypress_sleep
                
        """
        immediately launch then exit okay popups with these messages
        """
        if not debug_okay_messages:
            debug_okay_messages=[]
        self.debug_okay_messages=debug_okay_messages
        
        self.tui_state=TUI_STATE.FLOW_NAVIGATE
        
        """
        choice_popup describes all the content in a choice popup:
        {"text":text,
         "selected_index":index,
         "choices": [{"label":text,
                      "attr": curses_attr,
                      "function":function_upon_click},
                     ...]
         }
        """            
        self.choice_popup={}
        
        "any missing values in tui config become default"
        self.tui_config=tui_config if tui_config else get_mflow_config()
        
        "append to this list at any time, and an 'okay' popup with this message will appear soon."
        self.messages=[]
        
        self.curses_setup_fail_message=""
        
        "if there are too many popup choices to show, this is the index of the topmost visible choice."
        self.choices_popup_overflow_index=0
        
        self.experiment_refresh_interval=self.tui_config["FLOW_STATUS_REFRESH_SECONDS"]
        
        self.flow_offset_xy=[0,0]
        self.last_processed_c=""
        
        "The number of times in a row that we checked input but found no key."
        self.no_input_count=0
        
        self.text_flow=TextFlow(self.maestro_experiment,
                                self.tui_config,
                                tui_id=self.tui_id)
                
        "Apply default loop indexes to text flow, usually this is 0"
        self.apply_first_loop_indexes_to_text_flow()
        
        self.user_asked_to_exit=False
        self.user_asked_to_refresh=False
        self.has_scheduled_command=False
        
        "restore previous tui state if a restore file exists"
        self.restore_tui()
        
    def cleanup_old_tui_files(self):
        "Delete old files in tmp and mflow logs"
        max_age_days=7
        a="find %s -mtime +%s -delete"
        for folder in (TMP_FOLDER, LOG_FOLDER):
            cmd=a%(folder,max_age_days)
            run_shell_cmd(cmd)
        
    def start(self):
        "Start the main UI loop."
        wrapper(self._start)
    
    def set_tui_state(self,new_state):
        old_state=self.tui_state
        self.tui_state=new_state
        
        if old_state != new_state:
            self.rebuild_chunks()
                
    def is_node_collapsed(self,node):
        return self.text_flow.is_node_collapsed(node)
    
    def add_message(self,message):
        self.messages.append(message)
        logger.info(message)
        
    def setup_before_first_refresh(self):
        curses.start_color()
        curses.use_default_colors()
        
        "do not print built-in cursor"
        curses.curs_set(0)
        
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        
        self.theme_attrs={"edit":get_curses_attr_from_string(self.tui_config.get("EDIT_MODE_COLOR"),is_reversed=True,logger=logger),
                          "view":get_curses_attr_from_string(self.tui_config.get("VIEW_MODE_COLOR"),is_reversed=True,logger=logger),
                          "cursor":get_curses_attr_from_string(self.tui_config.get("CURSOR_COLOR"),is_reversed=True,logger=logger)}
        
        self.stdscr.nodelay(True)
        self.stdscr.clear()
        
        self.move_cursor(self.cursor_start_xy[0],self.cursor_start_xy[1])
        
        self.console_width=curses.COLS
        self.console_height=curses.LINES
        width=self.console_width
        height=self.console_height
        logger.debug("console dimensions (%s,%s)"%(width,height))
        
        if width<MINIMUM_CONSOLE_DIMENSIONS[0] or height<MINIMUM_CONSOLE_DIMENSIONS[1]:
            msg="Required minimum console dimensions %s were not met. To fix this, you can make your console window bigger, zoom out, or make the font size smaller. Dimensions = %s"
            msg=msg%(str(MINIMUM_CONSOLE_DIMENSIONS),str([self.console_width,self.console_height]))
            logger.error(msg)
            self.curses_setup_fail_message=msg
            return
                
        self.header_window=curses.newwin(1,width,0,0)
        self.flow_window=curses.newwin(height-2,width,1,0)
        self.footer_window=curses.newwin(1,width,height-1,0)
        
        self.text_flow.rebuild_experiment_chunks()
        flow_width,flow_height=self.text_flow.dimensions
        
        "the dimensions of the console dedicated to showing the flow"
        self.flow_window_height,self.flow_window_width=self.flow_window.getmaxyx()
        self.flow_window_size=(self.flow_window_width,self.flow_window_height)
        
        self.max_flow_offset_xy=[flow_width-width+1,flow_height-self.flow_window_height+1]
        "if flow is smaller than console, max offsets are 0"
        self.max_flow_offset_xy=[max(value,0) for value in self.max_flow_offset_xy]
        
        self.clamp_cursor_and_flow()
    
    def apply_first_loop_indexes_to_text_flow(self):
        for node_data in self.maestro_experiment.get_node_datas():
            node_path=node_data["path"]
            indexes=node_data["loop_indexes_available"]
            if indexes:
                first=indexes[0]
                self.text_flow.set_node_selected_loop_index(node_path,first)
    
    def exit_tui(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()           
    
    def rebuild_flow_chunks(self):      
        
        height,width=self.flow_window.getmaxyx()
        self.flow_window.erase()
        
        refresh_items=self.text_flow.chunks+self.cursor["chunks"]
        
        for item in refresh_items:
            x,y=item["xy"]
            text=item["text"]
            
            "window coordinates. for example, inner_x=0 for a far right text, if we have scrolled to the right"
            inner_x=x-self.flow_offset_xy[0]
            inner_y=y-self.flow_offset_xy[1]
            max_inner_x=inner_x+len(item["text"])
            
            "skip item if completely outside the window, given current offset"
            if inner_x+len(text)<0 or inner_x>=width or inner_y<0 or inner_y>=height:
                continue
            
            "cut off left of text if too far left"
            if inner_x<0:
                text=text[abs(inner_x):]
                inner_x=0
            
            "cut off right of text if too far right"
            extra_x=max(0,max_inner_x-width+1)
            if extra_x:
                text=text[:-extra_x]
            
            attr=item["curses_attr"]
            self.flow_window.addstr(inner_y,inner_x,text,attr)
        
        self.flow_window.refresh()
    
    def rebuild_header_chunks(self):
        clock_time=time.strftime('%H:%M:%S',time.localtime(self.last_experiment_refresh_time))
        
        if self.is_edit_mode:
            text="Edit suite mode. Press 'e' to go back to read-only mode."    
        else:
            text="mflow %s  '%s' on '%s' at %s"%(VERSION,
                                                 self.maestro_experiment.name,
                                                 self.maestro_experiment.datestamp,
                                                 clock_time)

        width=self.header_window.getmaxyx()[1]-1
        text=pad_text_with_spaces(text,width)        
        attr=self.theme_attrs["edit"] if self.is_edit_mode else self.theme_attrs["view"]
        
        self.header_window.addstr(0,0,text,attr)
        self.header_window.refresh()
    
    def rebuild_footer_chunks(self):
        
        x,y=self.cursor["xy"]
        node_on_cursor=self.text_flow.get_node_path_from_xy(x,y)
        if node_on_cursor:
            text=" Node: "+node_on_cursor
        else:           
            text=" Press 'q' to quit."
        
        "fill the rest of the bar with whitespace"
        width=self.footer_window.getmaxyx()[1]
        text=text+" "*(width-len(text)-1)        
        attr=self.theme_attrs["edit"] if self.is_edit_mode else self.theme_attrs["view"]
        
        self.footer_window.addstr(0,0,text,attr)
        self.footer_window.refresh()
        
    def rebuild_choice_popup_chunks(self):
        
        if self.tui_state != TUI_STATE.CHOICE_POPUP:
            return
        
        choices=self.choice_popup["choices"]
        console_width,console_height=get_console_dimensions()
        width=min(90,console_width)
        max_height=max(20,console_height-10)
        min_x=int(console_width/2-width/2)        
        
        "count how many lines we need for this message"
        message_lines=[]
        if self.choice_popup["text"]:
            text=self.choice_popup["text"]
            line_width=width-4
            message_lines=get_text_lines_within_width(text,line_width)
        message_height=len(message_lines)
        
        """
        This is the number of lines of height in all popup height, which are not used by choices.
        Top border is 2 thick, plus prompt text, plus bottom border 2 thick.
        """
        not_choice_y_padding=6+message_height
        "the maximum number of choices a popup with this max_height can show"
        self.choice_popup_max_choice_count=max_height-not_choice_y_padding
        height=min(len(choices),self.choice_popup_max_choice_count)+not_choice_y_padding
        is_overflow=len(choices)>self.choice_popup_max_choice_count
        top=int((console_height-height)/2)
                
        self.popup_window=curses.newwin(height,width,top,min_x)
        self.popup_window.erase()
        
        "text prompt"
        for i,line in enumerate(message_lines):
            self.popup_window.addstr(2+i,2,line,0)
        
        "top border"
        top_border_text=self.choice_popup.get("top_border_text",
                                              "Select a choice and press enter.")
        header=pad_text_with_spaces(top_border_text,width)
        self.popup_window.addstr(0,0,header,curses.A_REVERSE)
                    
        "bottom border"
        is_scrolled_to_bottom=self.choices_popup_overflow_index+self.choice_popup_max_choice_count>=len(choices)
        if is_overflow and not is_scrolled_to_bottom:
            text=pad_text_with_spaces("(more)",width-4)
            self.popup_window.addstr(height-3,0,text,0)
        footer_has_text=self.choice_popup.get("bottom_border_text",True)
        if footer_has_text:
            footer=pad_text_with_spaces("Press 'c' to cancel.",width)
        else:
            footer=" "*width
        self.popup_window.addstr(height-2,0,footer,curses.A_REVERSE)
        
        "vertical borders"
        for y in range(1,height-1):
            for x in (0,width-1):
                self.popup_window.addstr(y,x," ",curses.A_REVERSE)
        
        "options"
        choice_start_y=3+message_height
        choice_start_x=2
        choices_to_show=choices[self.choices_popup_overflow_index:
            self.choices_popup_overflow_index+self.choice_popup_max_choice_count]
            
        center_choice_text=self.choice_popup.get("center_choice_text",False)
        for i,choice in enumerate(choices_to_show):
            
            label=choice["label"]
            x_offset=0
            if center_choice_text:
                x_offset=int(width/2-len(label)/2)
            
            attr=choice.get("attr",0)
            if i==self.choice_popup["selected_index"]-self.choices_popup_overflow_index:
                attr|=curses.A_REVERSE
            y=choice_start_y+i
            self.popup_window.addstr(y,choice_start_x+x_offset,label,attr)
                
        self.popup_window.refresh()
        
    def can_schedule_commands(self):
        """
        Returns true if this python script was launched by a wrapper bash command.
        This must be true for Python to launch bash commands outside curses or Python.
        """
        return os.environ.get("IS_MFLOW_LAUNCHED_FROM_WRAPPER")=="true"
        
    def schedule_command_outside_curses(self,cmd):
        """
        Commands like vim cannot be launched within the curses loop.
        This function sets flags to exit the curses loop, launch this
        bash command 'cmd', then return to the curses loop.
        """
        
        path=TMP_BASH_WRAPPER_COMMAND_FILE_PREFIX+self.tui_id
        if self.can_schedule_commands():
            safe_write(path,cmd)
            self.save_tui_restore_data()
            self.user_asked_to_exit=True
            self.has_scheduled_command=True
        else:
            logger.error("schedule_command_outside_curses failed because Python script was not launched with the wrapper bash script.")
            return
        
    def save_tui_restore_data(self):
        """
        Write a temporary file with full TUI state (like selected or collapsed nodes)
        so that a relaunch can resume.
        """
        
        tui_restore_data={"cursor_xy":self.cursor["xy"],
                          "node_states":self.text_flow.node_states,
                          "tui_state":self.tui_state}
        data=json.dumps(tui_restore_data)
        safe_write(self.tui_restore_data_path,data)
        logger.info("Saved tui_restore_data JSON to '%s'"%self.tui_restore_data_path)
    
    def restore_tui(self):
        """
        If a tui_restore_data is found, restore full TUI state from that.
        """
        
        path=self.tui_restore_data_path
        try:
            with open(path,"r") as f:
                data=f.read()
            j=json.loads(data)
        except:
            return
        
        "apply the restoration point"
        xy=j["cursor_xy"]     
        self.cursor_start_xy=xy
        
        self.text_flow.node_states=j["node_states"]        
        self.set_tui_state(j["tui_state"])
        
    def process_user_input(self):
        
        if self.debug_keypresses:
            for c in self.debug_keypresses:
                self.process_user_input_char(c)
                time.sleep(self.debug_keypress_sleep)
            self.debug_keypresses=[]
        
        if not self.allow_user_input:
            return
        
        if self.debug_okay_messages and self.tui_state != TUI_STATE.CHOICE_POPUP:
            message=self.debug_okay_messages.pop(0)
            
            "show the debug okay popup then press enter"
            self.popup_okay_message(message)
            self.debug_keypresses.append(ord("\n"))
            
            "quit after last debug okay message"
            if not self.debug_okay_messages:
                self.debug_keypresses.append(ord("q"))
        
        chars=[]
        c=self.stdscr.getch()
        
        """
        There is no concept of frames or keyup in curses.
        Here we count curses.ERR occurances in a row, if it passes a threshold count, that's like a keyup.
        """
        if c==curses.ERR:
            self.no_input_count+=1
            if self.no_input_count>4:
                self.last_processed_c=""
        else:
            self.no_input_count=0
            
        while c != curses.ERR:
            chars.append(c)
            c=self.stdscr.getch()
        
        for c in chars:
            self.process_user_input_char(c)
            
    def refresh_cursor(self):
        x,y=self.cursor["xy"]
        self.move_cursor(x,y)
    
    def move_cursor(self,x,y):
        self.cursor={"xy":[x,y],
                     "chunks":[]}
        
        is_nav_tree=self.tui_config["KEYBOARD_NAVIGATION"]==KEYBOARD_NAVIGATION_TYPE.TREE
        if is_nav_tree:            
            node_path=self.text_flow.get_node_path_from_xy(x,y)
            rect=self.text_flow.node_rects.get(node_path)
            if not node_path or not rect:
                logger.error("Cursor did not find any node rect, despite being in tree navigation mode. Highlightning nothing. '%s' (%s,%s)"%(node_path,x,y))
                return
            self.cursor["chunks"]=self.get_cursor_highlight_chunks_for_rect(rect)
                
        else:
            for i,j in CURSOR_POINTS:
                x2=x+i
                y2=y+j
                item={"text":" ",
                      "xy":(x2,y2),
                      "color":"",
                      "curses_attr":self.theme_attrs["cursor"]}
                self.cursor["chunks"].append(item)
    
    def set_edit_mode(self,is_edit_mode):
        logger.info("set edit mode: %s"%is_edit_mode)
        has_changed=self.is_edit_mode!=is_edit_mode
        if has_changed:
            self.is_edit_mode=is_edit_mode
            self.rebuild_footer_chunks()
            self.rebuild_header_chunks()
            
    def process_choice_popup_char(self,c):
        
        if c == curses.KEY_UP:
            self.choice_popup["selected_index"]-=1
        elif c == curses.KEY_DOWN:
            self.choice_popup["selected_index"]+=1
        elif c == curses.KEY_PPAGE:
            self.choice_popup["selected_index"]-=10
        elif c == curses.KEY_NPAGE:
            self.choice_popup["selected_index"]+=10
        elif c in (curses.KEY_ENTER,10):
            self.confirm_selected_popup_choice()
        elif chr(c) == "c":
            self.set_tui_state(TUI_STATE.FLOW_NAVIGATE)
        else:
            return

        self.clamp_popup_index()
        self.rebuild_chunks()   
        
    def process_coordinate_navigation_char(self,c):
        """
        If 'c' matches a coordinate navigation key, move the cursor.
        Returns true if a change occured.
        """
        
        navigation_speed=5 if c in NAVIGATION_KEYS and self.last_processed_c and c==self.last_processed_c else 1
        cursor_xy=self.cursor["xy"]
        
        if c == 10:
            self.on_enter_in_flow()
        elif c == curses.KEY_UP:
            cursor_xy[1]-=navigation_speed
        elif c == curses.KEY_DOWN:
            cursor_xy[1]+=navigation_speed
        elif c == curses.KEY_LEFT:
            cursor_xy[0]-=navigation_speed
        elif c == curses.KEY_RIGHT:
            cursor_xy[0]+=navigation_speed            
        elif c == curses.KEY_PPAGE:
            cursor_xy[1]-=20
        elif c == curses.KEY_NPAGE:
            cursor_xy[1]+=20
        elif c == curses.KEY_HOME:
            cursor_xy[0]=0
        elif c == curses.KEY_END:
            cursor_xy[0]=self.max_flow_offset_xy[0]
        else:
            return
        
        self.clamp_cursor_and_flow()
        self.rebuild_chunks()        
    
    def process_tree_navigation_char(self,c):
        """
        If 'c' matches a tree navigation key, move the cursor.
        """
        
        if c == 10:
            self.on_enter_in_flow()
            return
        
        cursor_xy=self.cursor["xy"]
        x,y=cursor_xy        
        current_node_path=self.text_flow.get_node_path_from_xy(x,y)
        if not current_node_path:
            logger.error("keyboard tree navigation failed. Cursor is not on any node, but it should always be.")
            return
        new_target_node=""
        
        "handle all cases up/down/left/right"
        if c == curses.KEY_UP:
            new_target_node=self.process_tree_navigation_up_down(True,current_node_path)
        elif c == curses.KEY_DOWN:
            new_target_node=self.process_tree_navigation_up_down(False,current_node_path)
        elif c == curses.KEY_LEFT:
            parent=self.maestro_experiment.get_parent(current_node_path)
            if parent:
                new_target_node=parent
        elif c == curses.KEY_RIGHT:
            node_data=self.maestro_experiment.get_node_data(current_node_path)
            children=node_data["flow_children_node_paths"]
            if children:
                new_target_node=children[0]
        
        "move cursor if new node"
        if new_target_node:
            rect=self.text_flow.node_rects.get(new_target_node)
            if rect:
                xy=[rect["min_x"],rect["min_y"]]
                
                "if we moved right and right was off screen, go max right to show full node."
                if c == curses.KEY_RIGHT:
                    xy[0]=rect["max_x"]
                    
                "similar logic as above, but down"
                if c == curses.KEY_DOWN:
                    xy[1]=rect["max_y"]
                
                self.move_cursor(xy[0],xy[1])            
                self.clamp_cursor_and_flow()
                self.rebuild_chunks()
                
    def process_tree_navigation_up_down(self,is_up,current_node_path):
        """
        In tree navigation mode, up/down was pressed.
        Returns the node_path that we should have selected after this keypress.
        """
        siblings=self.maestro_experiment.get_siblings(current_node_path)
        sibling_index=siblings.index(current_node_path)
        is_bjump=self.tui_config["NAVIGATION_BRANCH_JUMPS"]
        rect=self.text_flow.node_rects.get(current_node_path)
        
        if is_up:
            sibling_index-=1
        else:
            sibling_index+=1
        
        "if we scrolled too high, loop, or jump"
        if sibling_index<0:
            if is_bjump:
                x,y=rect["center_x"],rect["min_y"]-1
                jump_target=self.get_branch_jump_target(x,y,is_up=True)
                if jump_target:
                    return jump_target
                return current_node_path
            else:
                sibling_index=len(siblings)-1
        
        "if we scrolled too low, loop, or jump"
        if sibling_index>=len(siblings):
            if is_bjump:
                x,y=rect["center_x"],rect["max_y"]+1
                jump_target=self.get_branch_jump_target(x,y,is_up=False)
                if jump_target:
                    return jump_target
                return current_node_path
            else:
                sibling_index=0
        
        return siblings[sibling_index]
    
    def get_branch_jump_target(self,start_x,start_y,is_up):
        """
        Starting at (x,y), scans either up or down
        to find the nearest node to (x,y)
        Returns None if no node is found.
        """
        logger.debug("get_branch_jump_target (%s,%s) is_up=%s"%(start_x,start_y,is_up))
        "find all rects within a large box above/below this point"
        rects={}
        
        "define the box we will scan"
        half_width=10+self.tui_config["NODE_ARROW_DASH_COUNT"]
        height=4*self.tui_config["NODE_MARGIN_BOTTOM"]
        min_x=start_x-half_width
        max_x=start_x+half_width
        
        if is_up:
            min_y=start_y-height
            max_y=start_y
        else:
            min_y=start_y
            max_y=start_y+height
            
        "find all node_path rects within that box"
        for node_path,rect in self.text_flow.node_rects.items():
            if rect["max_x"]<min_x:
                continue
            if rect["min_x"]>max_x:
                continue
            if rect["max_y"]<min_y:
                continue
            if rect["min_y"]>max_y:
                continue
            rects[node_path]=rect
            
        "find the node_path with the smallest distance"
        best_distance=0
        best_node_path=""
        
        for node_path,rect in rects.items():
            
            "sideways distance costs more"
            distance=abs(start_x-rect["center_x"])*2+abs(start_y-rect["center_y"])
            
            if not best_node_path or distance<best_distance:
                best_distance=distance
                best_node_path=node_path
                
        return best_node_path
                
    def debug_input_char(self,c):
        """
        this function is called when TuiManager.is_debug is True, 
        and the user pressed this char on the keyboard.
        """
        
        if chr(c)=="1":
            self.popup_okay_message("short message")
        if chr(c)=="2":
            self.popup_okay_message("this is a long message "*10)
        if chr(c)=="3":
            self.popup_okay_message("this is a long message "+"that-has-a-huge-thingermajigger-in-it-"*5)
    
    def process_user_input_char(self,c):
        "Where c is a curses key code from getch"
        
        "exit"
        if chr(c) in "xq":
            self.user_asked_to_exit=True
            return
        
        if chr(c) in "e" and self.tui_state==TUI_STATE.FLOW_NAVIGATE:
            self.set_edit_mode(not self.is_edit_mode)
            return
        
        if chr(c) in "r":
           self.user_asked_to_refresh=True
           return
       
        if self.is_debug:
            self.debug_input_char(c)            
        
        if self.tui_state==TUI_STATE.FLOW_NAVIGATE:
                
            is_nav_coord=self.tui_config["KEYBOARD_NAVIGATION"]==KEYBOARD_NAVIGATION_TYPE.COORDINATE
            is_nav_tree=self.tui_config["KEYBOARD_NAVIGATION"]==KEYBOARD_NAVIGATION_TYPE.TREE
            
            if is_nav_coord:
                self.process_coordinate_navigation_char(c)
            elif is_nav_tree:
                self.process_tree_navigation_char(c)
            else:
                raise NotImplementedError
                
        elif self.tui_state==TUI_STATE.CHOICE_POPUP:
            self.process_choice_popup_char(c)
        
        self.last_processed_c=c
    
    def clamp_popup_index(self):
        
        if self.tui_state != TUI_STATE.CHOICE_POPUP:
            return
        
        index=self.choice_popup["selected_index"]
        
        if index<0:
            index=len(self.choice_popup["choices"])-1
            
        if index>=len(self.choice_popup["choices"]):
            index=0
        
        "too many choices to show, and we went higher than highest"
        min_choice_index_shown=self.choices_popup_overflow_index
        if index<min_choice_index_shown:
            self.choices_popup_overflow_index=index
        
        "too many choices to show, and we went lower than lowest"
        max_choice_index_shown=self.choices_popup_overflow_index+self.choice_popup_max_choice_count-1
        if index>max_choice_index_shown:
            self.choices_popup_overflow_index=index-self.choice_popup_max_choice_count+1
        
        self.choice_popup["selected_index"]=index
        
        logger.info("selected_index = %s choices_popup_overflow_index = %s"%(index,self.choices_popup_overflow_index))
            
    def on_enter_in_flow(self):
        "called when the user presses enter in the flow navigation state"
        
        x,y=self.cursor["xy"]
        node_path=self.text_flow.get_node_path_from_xy(x,y)        
        if node_path:
            logger.debug("selecting node:\n"+pretty(self.maestro_experiment.get_node_data(node_path)))
            self.popup_select_node(node_path)
            
    def get_cursor_highlight_chunks_for_rect(self,rect):
        chunks=[]
        
        "horizontal bars"
        for y in (rect["max_y"]+1,rect["min_y"]-1):
            chunk={"text":" "*rect["width"],
                  "xy":(rect["min_x"],y),
                  "color":"",
                  "curses_attr":self.theme_attrs["cursor"]}
            chunks.append(chunk)
        
        "vertical bars"
        for x in (rect["max_x"]+1,rect["min_x"]-1):
            for y in range(rect["min_y"]-1,rect["max_y"]+2):
                chunk={"text":" ",
                      "xy":(x,y),
                      "color":"",
                      "curses_attr":self.theme_attrs["cursor"]}
                chunks.append(chunk)
        
        return chunks
    
    def clamp_cursor_and_flow(self):
        """
        For coordinate navigation, clamp the cursor to within the flow window.
        For tree navigation, clamp the cursor to root if it's not on a node.
        Also, change flow offset if cursor hit the edge.
        """
        
        if self.tui_state != TUI_STATE.FLOW_NAVIGATE:
            return
        
        xy=self.cursor["xy"]
        
        if self.tui_config["KEYBOARD_NAVIGATION"]==KEYBOARD_NAVIGATION_TYPE.TREE:   
            x,y=xy
            current_node_path=self.text_flow.get_node_path_from_xy(x,y)
            if not current_node_path:
                new_xy=self.text_flow.get_xy_from_node_path(self.maestro_experiment.root_node_path)
                xy[0]=new_xy[0]
                xy[1]=new_xy[1]

        flow_dimensions=self.text_flow.dimensions
        
        for i in range(2):            
            
            "set cursor to always be inside flow min/max"
            xy[i]=clamp(xy[i],0,flow_dimensions[i])
            
            "clamp for cases where cursor is left or above boundary"
            self.flow_offset_xy[i]=min(self.flow_offset_xy[i],xy[i])
            
            "clamp for cases where cursor is right or below boundary"
            self.flow_offset_xy[i]=max(self.flow_offset_xy[i],xy[i]-self.flow_window_size[i]+1)
        
        self.move_cursor(xy[0],xy[1])
    
    def refresh_statuses(self):
        self.last_experiment_refresh_time = time.time()
        self.text_flow.refresh_status_color_for_nodes()
        self.rebuild_chunks()
        
    def rebuild_chunks(self):
        self.rebuild_flow_chunks()
        self.rebuild_header_chunks()
        self.rebuild_footer_chunks()
        self.rebuild_choice_popup_chunks()
    
    def _start(self,stdscr):
        self.stdscr=stdscr
        
        self.setup_before_first_refresh()
        if self.curses_setup_fail_message:
            print(self.curses_setup_fail_message)            
            return
        
        interval=1/60
        
        is_first=True
        while True:
            self.process_user_input()
            
            if is_first:
                self.rebuild_chunks()
                is_first=False
            
            if self.user_asked_to_exit:
                self.exit_tui()
                break
            
            if self.user_asked_to_refresh:
                self.refresh_statuses()
            
            delta=time.time()-self.last_experiment_refresh_time
            if self.user_asked_to_refresh or delta > self.experiment_refresh_interval:
                self.user_asked_to_refresh=False
                self.refresh_statuses()
                
            time.sleep(interval)
