import configparser

def read(section,key):
    try:
        #print('starting')
        config = configparser.ConfigParser()
        #print('config set')
        f = open(r'config.cfg')
        #print('file openned', f)
        config.read_file(f)
        #print('config read')
        r = config.get(section,key)
        #print('config get ok')
    except:
        return 0
    return r

# IP = read('IP', 'client_ip')
# print(IP, type(IP))