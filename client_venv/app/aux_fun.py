import requests
import configparser
from os import path
import re

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

def verifyPV(pv):
    url = read('EPICS','url')
    r = requests.get(url, allow_redirects=True, verify=False)
    fullpvlist = r.text.replace('"','').split(',')
    r = re.compile(pv)
    matched_pv_list = list(filter(r.match, fullpvlist))

    if matched_pv_list:
        print('match')
        return 1
    else:
        print('n match')
        return 0

#verifyPV('TS-01:PS-CV-1:Current-Mon')