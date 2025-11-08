import os
import configparser


base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "configuration.ini")
config_path = os.path.normpath(config_path)

config = configparser.ConfigParser()
config.read(config_path)