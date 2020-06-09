
"""
This code handles flow reading for the MaestroExperiment class.

This class contains and finds information that can only be known about an experiment if a datestamp is given.

This abstract class is not meant to be instantiated, only inherited.
"""

from maestro.node_log_parser import NodeLogParser

class ME_Snapshot():
    
    def set_snapshot(self,datestamp):
        
        assert len(datestamp)==10
        self.datestamp=datestamp
        self.long_datestamp=datestamp[::-1].zfill(14)[::-1]
        
        node_log_path=self.path+"/logs/"+self.long_datestamp+"_nodelog"
        self.node_log_parser=NodeLogParser(node_log_path,
                                           refresh_interval=self.node_log_refresh_interval)
        