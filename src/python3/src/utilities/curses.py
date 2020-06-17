import curses

from mflow.utilities import logger
from constants.curses import STATUS_TO_CURSES_COLOR
from constants.colors import CURSES_COLOR_INDEX

def get_curses_attr_from_color(curses_color_index,is_reversed=True):
    try:
        "this will fail if curses is not initialized"
        attr=curses.color_pair(curses_color_index)
        
        "reverse the background and foreground colors"
        if is_reversed:
            attr |= curses.A_REVERSE
            
        return attr
    except curses.error:

        "for some reason this happens a lot, until it is resolved, only log once per launch"
        try:
            get_curses_attr_from_color.curses_error_count
        except AttributeError:
            get_curses_attr_from_color.curses_error_count=0
        get_curses_attr_from_color.curses_error_count+=1
        if get_curses_attr_from_color.curses_error_count==0:
            logger.error("get_curses_attr_from_color failed. Maybe curses is not init yet? index = '%s'"%curses_color_index)

        return 0

def get_curses_attr_from_string(color_string,default=0,is_reversed=False):
    "Given a string like 'ORANGE' returns the curses color attr."
    index=CURSES_COLOR_INDEX.__dict__.get(color_string.upper(),default)
    return get_curses_attr_from_color(index,is_reversed=is_reversed)

def get_curses_attr_from_status(status,is_reversed=True):
    color=STATUS_TO_CURSES_COLOR.get(status,CURSES_COLOR_INDEX.GREY)        
    return get_curses_attr_from_color(color,is_reversed=is_reversed)

def get_console_dimensions():
    "returns a tuple (width,height) for the current console dimensions"
    return curses.COLS,curses.LINES

