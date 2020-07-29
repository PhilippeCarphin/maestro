import platform
import random

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


def print_color(text, color=0, end="\n"):
    if platform.system() != "Linux":
        print(text, end=end)
    prefix = ""
    if color:
        prefix += "\033[%sm" % (color - 10)

    print(prefix + str(text) + "\033[0m", end=end)


def print_blue(text, end="\n"):
    print_color(text, COLORS.BLUE, end=end)


def print_orange(text, end="\n"):
    print_color(text, COLORS.ORANGE, end=end)


def print_red(text, end="\n"):
    print_color(text, COLORS.RED, end=end)


def print_green(text, end="\n"):
    print_color(text, COLORS.GREEN, end=end)


def print_yellow(text, end="\n"):
    print_color(text, COLORS.YELLOW, end=end)
