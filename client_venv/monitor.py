# -*- coding: utf-8 -*-
# #Rodar esse script na máquina que for rodar o cliente
import sqlite3, re, client, writer, requests, configparser
from os import path
from datetime import datetime, timedelta
from epics import caget
from time import sleep
from app.dbfun import get_notifications_db, set_sent_db, set_sent_time_db, get_fullpvlist_connection
from app.db.db.init_fullpvlist import update_db

class notification():
    def __init__(self, id, created, expiration, pv, rule, limits, owner, \
                 phone, sent, sent_time, interval, persistent):
        self.id = id
        self.created = created
        self.expiration = expiration
        self.pv = pv
        self.rule = rule
        self.limits = limits
        self.owner = owner
        self.phone = phone
        self.sent = sent
        self.sent_time = sent_time
        self.interval = interval
        self.persistent = persistent

def find_val(limit):
    val = ''
    for char in limit:
        if (char.isnumeric() or char=='.' or char==','):
            val = val + char
        else:
            val = val.replace(',','.')
            return val
    val = val.replace(',','.')
    return val

def ext_lim(limits):
    L = dict.fromkeys(['L', 'LL', 'LU'])
    try:
        mL = re.search(r'\AL=', limits)
        #teste for 'L='
        if mL:
            L['L'] = float(limits[mL.span()[1]:])
        #teste for 'LL='
        mLL = re.search('LL=', limits)
        if mLL:
            L['LL'] = float(find_val(limits[mLL.span()[1]:]))
        #teste for 'LU='
        mLU = re.search('LU=', limits) 
        if mLU:
            L['LU'] = float(find_val(limits[mLU.span()[1]:]))
        return L
    except:
        mL = re.search(r'\AL=', limits)
        L['L'] = limits[mL.span()[1]:]
        #print('L except =', L['L'])
        return L

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

def getfullpvlist(): # gets the list from fullpvlist_db
    conn_fullpvlist = get_fullpvlist_connection()
    fullpvlist = conn_fullpvlist.execute('SELECT pv FROM fullpvlist_db').fetchall()
    m = []
    for row in fullpvlist:
        for i in row:
            m.append(i)
    return m

def evaluate():
    if update_db():
        fullpvlist = getfullpvlist()
        while True:
            now = datetime.now()
            notifications = get_notifications_db()
            for row in notifications:
                n =  notification(id=row['id'],\
                                  created=row['created'],\
                                  expiration=row['expiration'],\
                                  pv=row['pv'],\
                                  rule=row['rule'],\
                                  limits=row['limits'],\
                                  owner=row['owner'],\
                                  phone=row['phone'],\
                                  sent=row['sent'],\
                                  sent_time=row['sent_time'],\
                                  interval=row['interval'],\
                                  persistent=row['persistent'])
                exp = datetime.strptime(n.expiration, "%Y-%m-%d %H:%M:%S")
                #print(exp, n.expiration)
                #print(n.sent_time)
                r = re.compile(n.pv)
                matchedpvlist = list(filter(r.match, fullpvlist)) #make a list of PVs matching the filter
                #print(matchedpvlist)
                if (now <= exp):
                    for matchedpv in matchedpvlist:
                        pv = caget(matchedpv) #get pv value
                        #print(n.pv, pv)
                        #print('created', n.created)
                        L = ext_lim(n.limits)['L']
                        LL = ext_lim(n.limits)['LL']
                        LU = ext_lim(n.limits)['LU']
                        #print('type:', type(pv))
                        if (type(pv)==int or type(pv)==float):
                            #print('evaluated rule for pv', n.pv, eval(n.rule))
                            if (eval(n.rule)):
                                msg = '{{"pv" : "{pv}",\
                                        "value" : "{value}",\
                                        "rule" : "{rule}",\
                                        "limits" : "{limits}",\
                                        "phone" : "{phone}",\
                                        "owner" : "{owner}"}}'.format(pv=matchedpv,\
                                                                    value=pv,\
                                                                    rule=n.rule,\
                                                                    limits=n.limits,\
                                                                    phone=n.phone,\
                                                                    owner=n.owner)
                                if (n.sent==False): #SMS not sent yet
                                    sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f")
                                    #print('sent_time', sent_time)
                                    #print(now, (sent_time + timedelta(minutes=int(n.interval))))
                                    if (now > (sent_time + timedelta(minutes=int(n.interval)))):
                                        r = client.client(msg) #send data to Server (modem's PC)
                                        #print("r:", r)
                                        if r==False:
                                            log = str(datetime.now()) + ' error sending message to server\n\r'
                                            dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                            log_path = path.join(dir_path, 'log.txt')
                                            writer.write(log_path, log, 'a')
                                        else:
                                            log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server\n\r'
                                            dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                            log_path = path.join(dir_path, 'log.txt')
                                            writer.write(log_path, log, 'a')
                                            set_sent_db(n.id, True)
                                            set_sent_time_db(n.id, now)
                                else: #SMS already sent
                                    if (n.persistent):
                                        sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f")
                                        #print('sent_time', sent_time)
                                        if (now > (sent_time + timedelta(minutes=int(n.interval)))):
                                            r = client.client(msg) #send data to Server (modem's PC)
                                            if r==False:
                                                log = str(datetime.now()) + ' error sending message to server\n\r'
                                                dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                                log_path = path.join(dir_path, 'log.txt')
                                                writer.write(log_path, log, 'a')
                                            else:
                                                log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server\n\r'
                                                dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                                log_path = path.join(dir_path, 'log.txt')
                                                writer.write(log_path, log, 'a')
                                                set_sent_db(n.id, True)
                                                set_sent_time_db(n.id, now)
                        if (type(pv)==str or type(pv)==None):
                            msg = '{{"pv" : "{pv}",\
                                    "value" : "{value}",\
                                    "rule" : "{rule}",\
                                    "limits" : "{limits}",\
                                    "phone" : "{phone}",\
                                    "owner" : "{owner}"}}'.format(pv=matchedpv,\
                                                                value=pv,\
                                                                rule=n.rule,\
                                                                limits=n.limits,\
                                                                phone=n.phone,\
                                                                owner=n.owner)
                            if (n.sent==False): #SMS not sent yet
                                sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f")
                                print('sent_time', sent_time)
                                if (now > (sent_time + timedelta(minutes=int(n.interval)))):
                                    r = client.client(msg) #send data to Server (modem's PC)
                                    if r==False:
                                        log = str(datetime.now()) + ' error sending message to server\n\r'
                                        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                        log_path = path.join(dir_path, 'log.txt')
                                        writer.write(log_path, log, 'a')
                                    else:
                                        log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server\n\r'
                                        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                        log_path = path.join(dir_path, 'log.txt')
                                        writer.write(log_path, log, 'a')
                                        set_sent_db(n.id, True)
                                        set_sent_time_db(n.id, now)
                            else: #SMS already sent
                                if (n.persistent):
                                    sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f")
                                    #print('sent_time', sent_time)
                                    if (now > (sent_time + timedelta(minutes=int(n.interval)))):
                                        r = client.client(msg) #send data to Server (modem's PC)
                                        if r==False:
                                            log = str(datetime.now()) + ' error sending message to server\n\r'
                                            dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                            log_path = path.join(dir_path, 'log.txt')
                                            writer.write(log_path, log, 'a')
                                        else:
                                            log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server\n\r'
                                            dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                            log_path = path.join(dir_path, 'log.txt')
                                            writer.write(log_path, log, 'a')
                                            set_sent_db(n.id, True)
                                            set_sent_time_db(n.id, now)
            sleep(10)

evaluate()