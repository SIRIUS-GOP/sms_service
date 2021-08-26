import configparser
from os import path

def read(section,key):
    try:
        config = configparser.RawConfigParser()
        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
        config_path = path.join(dir_path, 'config.cfg')
        config.read_file(open(config_path)) 
        r = config.get(section,key)
    except:
        return 0
    return r


# IP = read('IP', 'client_ip')
# print(IP, type(IP))
