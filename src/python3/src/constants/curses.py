import curses 
from constants.maestro import NODE_STATUS
from constants.colors import CURSES_COLOR_INDEX

"The minimum console dimensions where mflow is guaranteed to work. Chosen pretty arbitrarily."
MINIMUM_CONSOLE_DIMENSIONS=[70,30]


STATUS_TO_CURSES_COLOR={NODE_STATUS.ABORT:CURSES_COLOR_INDEX.RED,
                        NODE_STATUS.SUBMIT_FAILURE:CURSES_COLOR_INDEX.RED,
                        NODE_STATUS.BEGIN:CURSES_COLOR_INDEX.GREEN,
                        NODE_STATUS.END:CURSES_COLOR_INDEX.BLUE,
                        NODE_STATUS.NOT_STARTED:CURSES_COLOR_INDEX.GREY,
                        NODE_STATUS.CATCHUP:CURSES_COLOR_INDEX.PURPLE,
                        NODE_STATUS.WAITING:CURSES_COLOR_INDEX.ORANGE}