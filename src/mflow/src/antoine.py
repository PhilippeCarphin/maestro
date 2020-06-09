#!../venv/bin/python3

from maestro.xml import get_combined_flow_for_experiment_path
from utilities import pretty
path="/home/smco500/.suites/gdps/g0/"
lxml_element=get_combined_flow_for_experiment_path(path)
print(pretty(lxml_element))


from maestro import MaestroExperiment

me=MaestroExperiment(path)

print("\n\nlxml element:")
print(me.root_flow)
