import sqlite3, os, requests

def read(section,key):
    try:
        config = configparser.RawConfigParser()
        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
        #print('dir_path ', dir_path)
        config_path = path.join(dir_path, 'config.cfg')
        #print('config_path ', config_path)
        config.read_file(open(config_path)) 
        r = config.get(section,key)
    except:
        return 0
    return r

def getfullpvlist():
    url = 'https://10.0.38.42/mgmt/bpl/getAllPVs?limit=-1'
    r = requests.get(url, allow_redirects=True, verify=False)
    #[item for item in list if condition]
    fullpvlist = r.text.replace('"','').split(',')
    return fullpvlist

dir_path = os.path.dirname(os.path.realpath(__file__)) #current folder application path
stripped_path = os.path.dirname(dir_path)
db_path = os.path.join(stripped_path, 'fullpvlist.db')
connection = sqlite3.connect(db_path)

sql_path = os.path.join(dir_path, 'schema_fullpvlist.sql')
with open(sql_path) as f:
    connection.executescript(f.read())

cur = connection.cursor()

fullpvlist = getfullpvlist()

for pv in fullpvlist:
    cur.execute("INSERT INTO fullpvlist_db (pv) VALUES (?)", (pv,))

print('done')
connection.commit()
connection.close()