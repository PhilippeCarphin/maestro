import pymaestro as pm

print("pymestro_example: I am going to make a call to a C function")
datestamp = '20190223102400'
node_path = '/main/cleanup/seqcleanup/'
exp_home = '/Users/pcarphin/Documents/GitHub/maestro/exp/r1_7.0.0'
pm.nodeinfo(
    node_path, # node
    '0', #filters
    'unused', # loops
    exp_home, #exp_homeh
    'unused',
    datestamp,
    'unused'
    )
print("pymaestro_example: I am back to the python code")
