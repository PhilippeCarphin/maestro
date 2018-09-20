import time

from utilities.colors import *

class ProgressTicker:
    """Prints characters if it has been long enough since the last print.
    Interval is in seconds.
    update_strings is a list of things to print, on loop. Leave as None for default.
    """
    def __init__(self,interval=1,update_strings=None):
        if not update_strings:
            update_strings=[(" "*abs(10-i)+"O") for i in range(20)]
        self.update_strings=update_strings
        self.interval=interval
        self.last_tick_time=time.time()
        self.last_printed_index=0
    
    def tick(self):
        if self.last_tick_time<time.time()-self.interval:
            print_yellow("       "+self.update_strings[self.last_printed_index])
            self.last_tick_time=time.time()            
            self.last_printed_index+=1
            self.last_printed_index%=len(self.update_strings)