from datetime import datetime
from os import path

def write(r):
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    log_path = path.join(dir_path, 'log.txt')
    f = open(log_path, "a")
    r = r.replace('\n\r', ' // ')
    r = str(datetime.now()) + ' // ' + r + '\n\r'
    f.write(r)
    f.close()