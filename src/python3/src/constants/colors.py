
class CURSES_COLOR_INDEX:
    """
    Beware of adding more colors.
    In some mobaxterm/windows setups, 1 and 9 to 32 is invisible, and 33+ is generally black/white.
    """
    GREY = 0
    RED = 2
    GREEN = 3
    ORANGE = 4
    BLUE = 5
    PURPLE = 6
    AQUA = 7
    SILVER = 8


CURSES_COLOR_INDEXES = (CURSES_COLOR_INDEX.GREY,
                        CURSES_COLOR_INDEX.RED,
                        CURSES_COLOR_INDEX.GREEN,
                        CURSES_COLOR_INDEX.ORANGE,
                        CURSES_COLOR_INDEX.BLUE,
                        CURSES_COLOR_INDEX.PURPLE,
                        CURSES_COLOR_INDEX.SILVER)


class COLORS:
    RED = 41
    GREEN = 42
    ORANGE = 43
    BLUE = 44
    PURPLE = 45
    AQUA = 46
    SILVER = 47
    GREY = 100
    PINK = 101
    LIME = 102
    YELLOW = 103
    SKY = 104
    MAGENTA = 105
    TURQUOISE = 106
    WHITE = 107
