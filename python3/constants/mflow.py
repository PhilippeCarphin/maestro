import curses


class TUI_STATE:
    """
    This is an enum for user interface states.
    The TUI is always in exactly one of these states.
    """

    "the regular view where you can navigate around the flow"
    FLOW_NAVIGATE = 1

    "a multiple choice popup is being shown, navigation is disabled"
    CHOICE_POPUP = 2


class KEYBOARD_NAVIGATION_TYPE:
    TREE = "tree"
    COORDINATE = "coordinate"


NAVIGATION_KEYS = set((curses.KEY_UP,
                       curses.KEY_DOWN,
                       curses.KEY_LEFT,
                       curses.KEY_RIGHT,
                       curses.KEY_PPAGE,
                       curses.KEY_NPAGE,
                       curses.KEY_HOME,
                       curses.KEY_END))