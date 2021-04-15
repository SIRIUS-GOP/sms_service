# -*- coding: utf-8 -*-
# #Rodar esse script na máquina que for rodar o cliente
import sqlite3, re, client, writer
from os import path
from datetime import datetime, timedelta
from epics import caget
from time import sleep
from app.dbfun import get_notifications_db, set_sent_db, set_sent_time_db

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
    mL = re.search(r'\AL=', limits)
     #teste for 'L='
    if mL:
        L['L'] = float(find_val(limits[mL.span()[1]:]))
    #teste for 'LL='
    mLL = re.search('LL=', limits)
    if mLL:
        L['LL'] = float(find_val(limits[mLL.span()[1]:]))
    #teste for 'LU='
    mLU = re.search('LU=', limits) 
    if mLU:
        L['LU'] = float(find_val(limits[mLU.span()[1]:]))
    return L

def evaluate():
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
            pv = caget(n.pv) #get pv value
            #print(n.pv, pv)
            #print(datetime.now(), n)
            L = ext_lim(n.limits)['L']
            LL = ext_lim(n.limits)['LL']
            LU = ext_lim(n.limits)['LU']
            if (now <= exp):
                if (eval(n.rule)):
                    msg = '{{"pv" : "{pv}",\
                             "value" : "{value}",\
                             "rule" : "{rule}",\
                             "limits" : "{limits}",\
                             "phone" : "{phone}",\
                             "owner" : "{owner}"}}'.format(pv=n.pv,\
                                                           value=pv,\
                                                           rule=n.rule,\
                                                           limits=n.limits,\
                                                           phone=n.phone,\
                                                           owner=n.owner)
                    if (n.persistent):
                        sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f")
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
                    else:
                        if (n.sent==False):
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
                                set_sent_time_db(n.id, datetime.now())
        sleep(10)

evaluate()