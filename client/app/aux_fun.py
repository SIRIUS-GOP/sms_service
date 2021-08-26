import requests
import configparser
from os import path
import re, requests

def read(section,key):
    try:
        config = configparser.RawConfigParser()
        dir_path = path.dirname(path.realpath(__file__), ) #current folder application path
        #print('dir_path ', dir_path)
        config_path = path.join(dir_path, '..' , 'config.cfg')
        config.read_file(open(config_path)) 
        r = config.get(section,key)
    except:
        return 0
    return r

def getfullpvlist():
    url = read('EPICS','url')
    r = requests.get(url, allow_redirects=True, verify=False)
    #[item for item in list if condition]
    fullpvlist = r.text.replace('"','').split(',')
    return fullpvlist
