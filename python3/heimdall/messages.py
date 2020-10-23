
from collections import OrderedDict
from utilities import print_red, print_orange, print_yellow, print_green, print_blue

def print_scan_message(message):
    """
    Print a message dictionary produced by the heimdall scanner in a nice paragraph with colors.
    """
    char_color_functions = OrderedDict([("c", print_red),
                                        ("e", print_orange),
                                        ("w", print_yellow),
                                        ("i", print_green),
                                        ("b", print_blue)])
    c=message["code"][0].lower()
    f=char_color_functions[c]
    f(message["code"]+": "+message["label"])
    print(message["description"])