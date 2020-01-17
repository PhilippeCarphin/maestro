from os.path import expanduser
import configparser

#in Python 3 it will be configparser
configFilePath = 'config.cfg'
config = configparser.ConfigParser()
config.read(configFilePath)

# get the paths from the config file:
exp_path = str(config.get('PATHS', 'exp_path'))

home = expanduser("~")
exp_path = home + exp_path