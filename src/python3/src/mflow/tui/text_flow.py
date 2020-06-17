
"""
This class converts a MaestroExperiment into chunks of text with coordinates, for use by curses or print.
"""

import time
from collections import OrderedDict

from maestro.experiment import MaestroExperiment
from mflow.utilities import logger, get_config
from utilities.curses import get_curses_attr_from_status
from utilities import pretty, is_xy_in_rect
from constants import NODE_TYPE

class TextFlow():
    def __init__(self,
                 maestro_experiment,
                 tui_config=None,
                 debug=False,
                 tui_id=None):
        
        assert type(maestro_experiment) is MaestroExperiment
        self.maestro_experiment=maestro_experiment
        self.debug=debug
        
        if not tui_id:
            tui_id=str(time.time())
        self.tui_id=tui_id
        
        "any missing values in tui config become default"
        self.tui_config=tui_config if tui_config else get_config()
        
        """
        string is a list of text items with their coordinates to draw somewhere.
        Note: (0,0) is top left.
        {
            "text":text,
            "xy":(x,y),
            "curses_attr":""
        }
        """
        self.chunks=[]
        
        """
        key is node name
        value is a rect, the space this node occupies:
            {"min_x":0,
             "min_y":0,
             "max_x":0,
             "max_y":0,
             "center_x":0,
             "center_y":0,
             "width":0,
             "height":0}
        """
        self.node_rects={}        
        
        """
        This keeps track of collapsed nodes and selected loop indexes.
        key is full node name
        value is a dictionary that 'may' contain these keys:
            {"is_collapsed":True|False,
             "selected_loop_index":index}
        """
        self.node_states={}
        
        "true if rebuild chunks has been run once"
        self.is_built=False
        
        """
        key is node_path string
        value is a list of chunks (references to dict objects in self.chunks) whose color
        should reflect the status of this node
        """
        self.status_chunks_for_node_path={}
        
    def set_node_collapsed(self,node_path,is_collapsed,tui_manager=None):
        """
        Set a node to collapsed, or expanded (uncollapsed, default)
        """
        if node_path not in self.node_states:
            self.node_states[node_path]={}
        self.node_states[node_path]["is_collapsed"]=is_collapsed
        self.rebuild_experiment_chunks()
        if tui_manager:
            tui_manager.refresh_cursor()
        logger.info("set_node_collapsed "+pretty(self.node_states))
    
    def get_xy_from_node_path(self,node_path):
        "returns the top left (x,y) of the text box for this node_path"
        rect=self.node_rects.get(node_path)
        if not rect:
            return None
        return (rect["min_x"],rect["min_y"])
        
    def is_node_collapsed(self,node):
        return bool(self.node_states.get(node,{}).get("is_collapsed"))
        
    def set_node_selected_loop_index(self,node_path,index):
        """
        Set the loop index number for this full node path.
        """
                
        if node_path not in self.node_states:
            self.node_states[node_path]={}
        self.node_states[node_path]["selected_loop_index"]=index
        logger.debug("set_node_selected_loop_index self.node_states =\n"+pretty(self.node_states))
        self.rebuild_experiment_chunks()
    
    def get_selected_index_for_node(self,node_path):
        """
        Returns the loop index that is currently selected for this node.
        """
        
        return self.node_states.get(node_path,{}).get("selected_loop_index",0)
    
    def get_loop_index_selection(self,node_path):
        """
        For example if:
            node_path = module1/loop1/loop2/task1/task2
            loop1 has selected index 1
            loop2 has selected index 5
        returns {"loop1":1,"loop2":5}
        """
        chunks=[c for c in node_path.split("/") if c.strip()]
        result=OrderedDict()
        n=""
        for chunk in chunks:
            if n:
                n+="/"
            n+=chunk
            if self.maestro_experiment.has_indexes(n):
                index=self.get_selected_index_for_node(n)
                result[chunk]=index
        return result
    
    def get_string_flow(self,strip_trailing_spaces=True):
        """
        Usually the curses library will use the list of string items to build its text display.
        Instead, this function uses that list to return one giant string of what curses would show.
        Useful for automated testing. Ignores colors.
        """
        
        self.rebuild_experiment_chunks()
        
        width,height=self.dimensions
        grid=[[" " for x in range(width+1)] for y in range(height+1)]
        for item in self.chunks:
            text=item["text"]
            x,y=item["xy"]
            for x_offset,c in enumerate(text):
                grid[y][x+x_offset]=c
        
        lines=["".join(row) for row in grid]
        
        if strip_trailing_spaces:
            lines=[line.rstrip() for line in lines]
        return "\n".join(lines)
    
    def get_node_path_from_xy(self,x,y):
        """
        Given the (x,y) in the text map, returns the node_path found there, if any.
        This includes the whole node box.
        """
        
        if not self.is_built:
            self.rebuild_experiment_chunks()
        
        for node_path,rect in self.node_rects.items():
            if is_xy_in_rect(x,y,rect):
                return node_path
        return ""
    
    def rebuild_experiment_chunks(self):
        logger.info("rebuild_experiment_chunks")
        
        self.is_built=True
        self.chunks=[]
        self.dimensions=(0,0)
        self.node_rects={}
        self.status_chunks_for_node_path={}
        
        self.recursive_textify_node_path(self.maestro_experiment.root_module_name,1,1)
        self.refresh_status_color_for_nodes()
        
        self.calculate_flow_dimensions()
        
    def refresh_status_color_for_nodes(self):
        for node_path in self.maestro_experiment.get_node_paths():
            self.refresh_status_color_for_node(node_path)
    
    def refresh_status_color_for_node(self,node_path):
        """
        A node_path node has several text chunks, whose color should be its status.
        This changes the chunk data so its color reflects the current node status.
        """

        loop_index_selection=self.get_loop_index_selection(node_path)
        status=self.maestro_experiment.get_node_status(node_path,
                                                                loop_index_selection=loop_index_selection)
        attr=get_curses_attr_from_status(status)     
        for chunk in self.status_chunks_for_node_path.get(node_path,[]):
            chunk["curses_attr"]=attr
        
    def add_chunks_for_node(self,node_path,x,y):
        """
        Add all text chunks required for an entire node box.
        Returns a rect for the space this node occupies.
        """
        
        me=self.maestro_experiment
        node_data=me.get_node_data(node_path)
        if not node_data:
            logger.error("add_chunks_for_node got a bad node_path: '%s'"%node_path)
            return 0
        
        self.status_chunks_for_node_path[node_path]=[]
        label=node_data["name"]
        node_path=node_data["path"]
        new_node_chunks=[]
                
        "title"
        if node_data["type"]==NODE_TYPE.SWITCH:
            switch_index=me.get_switch_index_from_datestamp(node_data,self.maestro_experiment.datestamp)
            label+=" = %s"%switch_index            
        chunk={"text":label,
              "xy":(x,y),
              "curses_attr":0}
        new_node_chunks.append(chunk)
        
        "node type"
        if self.tui_config["FLOW_NODE_SHOW_TYPE"]:
            text="(%s)"%node_data["type"].lower().strip()
            chunk={"text":text,
              "xy":(x,y+len(new_node_chunks)),
              "curses_attr":0}
            new_node_chunks.append(chunk)
        
        "collapsed"
        if self.is_node_collapsed(node_path):
            chunk={"text":"(collapsed)",
              "xy":(x,y+len(new_node_chunks)),
              "curses_attr":0}
            new_node_chunks.append(chunk)
        
        "loop index"
        d=self.node_states.get(node_path,{})
        if "selected_loop_index" in d:
            selected_loop_index=d["selected_loop_index"]
            chunk={"text":"loop index = %s "%selected_loop_index,
              "xy":(x,y+len(new_node_chunks)),
              "curses_attr":0}
            new_node_chunks.append(chunk)
            
        "calculate width of widest text"
        width=max([len(node_chunk["text"]) for node_chunk in new_node_chunks])
        
        "add spaces padding to all text so node is rectangle"
        for node_chunk in new_node_chunks:
            node_chunk["text"]=node_chunk["text"]+" "*(width-len(node_chunk["text"]))
        
        
        self.chunks+=new_node_chunks
        
        height=len(new_node_chunks)
        rect={"min_x":x,
                "min_y":y,
                "max_x":x+width-1,
                "max_y":y+height-1,
                "width":width,
                "height":height}
        rect["center_x"]=int((rect["min_x"]+rect["max_x"])/2)
        rect["center_y"]=int((rect["min_y"]+rect["max_y"])/2)
        
        "add node rect to (x,y) lookup map"
        self.node_rects[node_path]=rect
        
        "cache all new chunks, since all these chunks should change color when its status changes"
        self.status_chunks_for_node_path[node_path]=new_node_chunks
        
        return rect
        
    def recursive_textify_node_path(self,node_path,left_x,top_y,used_paths=None):
        """
        Add the flow text strings for this node and all its children.
        (left_x,top_y) are the top left coordinates to start the branch.
        Returns the lowest y coordinate used to render this branch.
        """
        
        if not used_paths:
            used_paths=set()
        if node_path in used_paths:
            logger.error("Aborting textifying this flow branch because it seems to recurse. node_path '%s' has occurred twice."%node_path)
            return top_y
        used_paths.add(node_path)
        
        rect=self.add_chunks_for_node(node_path,left_x,top_y)
        me=self.maestro_experiment
        margin_bottom=self.tui_config["NODE_MARGIN_BOTTOM"]
        arrow_width=self.tui_config["NODE_ARROW_DASH_COUNT"]+2
        
        "draw children and arrows, if not collapsed"
        previous_lowest_y=top_y+rect["height"]-1
        if not self.is_node_collapsed(node_path):
            arrow_start_x=rect["max_x"]+2
            previous_arrow_y=top_y
            
            children=me.get_children(node_path)
            
            if me.is_switch(node_path):
                """
                A <SWITCH> may have many children <SWITCH_ITEM>
                however we only want to show the grandchildren of <SWITCH> for only one of its
                <SWITCH_ITEM> children. This is according to the current hour, or day of week.
                
                For example, the node paths suggest:
                    switch1 |--> 00 --> task1
                            |--> 12 --> task2
                
                However we want to show this:
                    switch1 |--> task1
                            |--> task2
                
                so here we replace children with grandchildren.
                """
                datestamp=self.maestro_experiment.datestamp
                child=me.get_switch_child_for_datestamp(node_path,datestamp)
                if child:
                    children=me.get_children(child)
                else:
                    children=[]
            
            for i,child in enumerate(children):
                child_start_y=top_y
                if i>0:
                    child_start_y=previous_lowest_y+margin_bottom+1
                    self.add_vertical_line(arrow_start_x,previous_arrow_y,child_start_y)
                child_start_x=self.add_arrow(arrow_start_x+1,child_start_y,width=arrow_width)+1
                lowest_y=self.recursive_textify_node_path(child,
                                                          child_start_x,
                                                          child_start_y,
                                                          used_paths=used_paths)
                previous_lowest_y=lowest_y
                previous_arrow_y=child_start_y
            
        return previous_lowest_y
    
    def add_arrow(self,start_x,y,width=7):
        """
        Returns rightmost x coordinate.
        width is the total width, including all characters.
        """
        width=max(width,2)
        arrow={"text":"-"*(width-2)+"> ",
              "xy":(start_x,y),
              "curses_attr":0}
        self.chunks.append(arrow)
        return start_x+width
    
    def add_vertical_line(self,x,y1,y2,char="|"):
        top_y=min(y1,y2)
        bottom_y=max(y1,y2)
        for y in range(top_y,bottom_y+1):
            line={"text":char,
                  "xy":(x,y),
                  "curses_attr":0}
            self.chunks.append(line)
        
    def calculate_flow_dimensions(self):
        """
        Iterate through all text items to find the largest x and y dimensions in the flow.
        """
        d=[0,0]
        for item in self.chunks:
            x,y=item["xy"]
            y+=item["text"].count("\n")
            max_x=x+len(item["text"])
            d=[max(max_x,d[0]),max(y,d[1])]
        self.dimensions=d
                
                
                
                
                
                
                