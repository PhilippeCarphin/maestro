import threading

from utilities.qstat import get_qstat_data
from home_logger import logger

def async_set_qstat_data_in_maestro_experiment(maestro_experiment):
    thread = threading.Thread(target=set_qstat_data_in_maestro_experiment,
                              args=(maestro_experiment,), 
                              kwargs={})
    thread.start()

def set_qstat_data_in_maestro_experiment(maestro_experiment):
    logger.debug("set_qstat_data_in_maestro_experiment started")
    maestro_experiment.qstat_data=get_qstat_data(logger=logger)
    logger.debug("set_qstat_data_in_maestro_experiment finished")
    