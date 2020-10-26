"""
The contents of this script are generally useful and can be copied, without modification, to other python projects.
"""

import platform
import random

from constants.colors import *


def print_color(text, color=0, end="\n"):
    if platform.system() != "Linux":
        print(text, end=end)
    prefix = ""
    if color:
        prefix += "\033[%sm" % (color - 10)

    print(prefix + str(text) + "\033[0m", end=end)


def print_orange(text, end="\n"):
    print_color(text, COLORS.ORANGE, end=end)


def print_blue(text, end="\n"):
    print_color(text, COLORS.BLUE, end=end)


def print_red(text, end="\n"):
    print_color(text, COLORS.RED, end=end)


def print_green(text, end="\n"):
    print_color(text, COLORS.GREEN, end=end)


def print_yellow(text, end="\n"):
    print_color(text, COLORS.YELLOW, end=end)
