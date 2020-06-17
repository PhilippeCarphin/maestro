"""
The contents of this script are generally useful and can be copied, without modification, to other python projects.
"""

import time

from utilities.colors import *


class Timer:
    # easy way to show updates every X number of seconds for big jobs.

    def __init__(self, interval, round_digits=1):
        self.start_time = time.time()
        self.last_time = self.start_time
        self.interval = interval

        if round_digits < 0:
            print("Warning, bad round_digits = '%s'" % round_digits)
            round_digits = 0

        self.round_digits = round_digits

    def tick(self, text):
        if time.time() > self.last_time + self.interval:
            self.last_time = time.time()
            print_color(text, COLORS.YELLOW)

    def stop(self, label):
        print_color(
            "%s took %s seconds." %
            (label, round(time.time() - self.start_time, self.round_digits)), COLORS.YELLOW)
