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
    def __init__(self, id, created, expiration, owner, phone, pv1, rule1, limits1, subrule1, pv2, \
                 rule2, limits2, subrule2, pv3, rule3, limits3, sent, sent_time, interval, persistent):
        self.id = id
        self.created = created
        self.expiration = expiration
        self.owner = owner
        self.phone = phone
        self.pv1 = pv1 #
        self.rule1 = rule1
        self.limits1 = limits1
        self.subrule1 = subrule1
        self.pv2 = pv2 #
        self.rule2 = rule2
        self.limits2 = limits2
        self.subrule2 = subrule2
        self.pv3 = pv3 #
        self.rule3 = rule3
        self.limits3 = limits3
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
        #test for 'L='
        if mL:
            L['L'] = float(limits[mL.span()[1]:])
        #test for 'LL='
        mLL = re.search('LL=', limits)
        if mLL:
            L['LL'] = float(find_val(limits[mLL.span()[1]:]))
        #test for 'LU='
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

def testpvlist(pvlist, rule, limits): #test pvs using rule and limits
    truelist = []
    pvvaluelist = []
    signal = False
    cageterror = 1
    #print('pvlist, rule, limits:', pvlist, rule, limits)
    for pv_ in pvlist:
        #print('pv_:', pv_)
        try:
            pv = caget(pv_)
            L = ext_lim(limits)['L']
            LL = ext_lim(limits)['LL']
            LU = ext_lim(limits)['LU']
            cageterror = 0
        except:
            cageterror = 1
        #print('L,LL,LU,pv', L, LL, LU, pv)
        #print('eval:', eval(rule))
        if cageterror != 1:
            try:
                if (eval(rule) and (type(pv)==int or type(pv)==float)):
                    truelist.append(pv_)
                    pvvaluelist.append(pv)
                    signal = True
            except:
                print('Error on eval(rule). pv:', pv_, 'L:', L, 'LL:', LL, 'and LU:', LU)
        else:
            print('Error on caget. PV:', pv_)
    aux = (signal, truelist, pvvaluelist)
    #print("signal, truelist, pvvaluelist", aux)
    return aux

def evaluate():
    if update_db():
        fullpvlist = getfullpvlist()
        while True:
            now = datetime.now()
            notifications = get_notifications_db()
            for row in notifications:
                n = notification(id=row['id'],\
                                 created=row['created'],\
                                 expiration=row['expiration'],\
                                 owner=row['owner'],\
                                 phone=row['phone'],\
                                 pv1=row['pv1'],\
                                 rule1=row['rule1'],\
                                 limits1=row['limits1'],\
                                 subrule1=row['subrule1'],\
                                 pv2=row['pv2'],\
                                 rule2=row['rule2'],\
                                 limits2=row['limits2'],\
                                 subrule2=row['subrule2'],\
                                 pv3=row['pv3'],\
                                 rule3=row['rule3'],\
                                 limits3=row['limits3'],\
                                 sent=row['sent'],\
                                 sent_time=row['sent_time'],\
                                 interval=row['interval'],\
                                 persistent=row['persistent'])
                exp = datetime.strptime(n.expiration, "%Y-%m-%d %H:%M:%S")
                #print(exp, n.expiration)
                #print(n.sent_time)
                r1 = re.compile(n.pv1)
                r2 = re.compile(n.pv2)
                #r3 = re.compile(n.pv3)
                matchedpvlist1 = list(filter(r1.match, fullpvlist)) #make a list of PVs matching the filter
                matchedpvlist2 = list(filter(r2.match, fullpvlist)) #make a list of PVs matching the filter
                #matchedpvlist3 = list(filter(r3.match, fullpvlist)) #make a list of PVs matching the filter
                #print('matchedpvlist1:', matchedpvlist1)
                #print('matchedpvlist2:', matchedpvlist2)
                #print('matchedpvlist3:', matchedpvlist3)
                if (now <= exp): #check expiration
                    #print(str(datetime.now()), "exp ok")
                    if (n.sent==False or (n.sent==True and n.persistent==True)): #check persistence and if it was sent b4
                        #print(n.pv1, n.subrule1, n.pv2, n.subrule2, n.pv3)
                        #print("check1:")
                        check1 = testpvlist(matchedpvlist1, n.rule1, n.limits1)
                        numpvs = 1
                        expr =  str(check1[0])
                        if (n.subrule1 != '0'):
                            #print("check2:")
                            check2 = testpvlist(matchedpvlist2, n.rule2, n.limits2)
                            if n.subrule1 == "not":
                                expr = expr + ' and (not ' + str(check2[0]) + ')'
                            else:
                                expr = expr + ' ' + n.subrule1 + ' ' + str(check2[0])      
                                #print('expression:', expr, 'rule:', n.rule2, 'limits:', n.limits2)                  
                            numpvs = 2
                        # if (n.subrule2 != '0'):
                        #     check3 = testpvlist(matchedpvlist3, n.rule2, n.limits3)
                        #     if n.subrule2 =="not":
                        #         expr = expr + ' and (not ' + str(check3[0]) + ')'
                        #     else:
                        #         expr = expr + ' ' + n.subrule2 + ' ' + str(check3[0])
                        #     numpvs = 3
                        #print("expression:", expr)
                        if (eval(expr)): #check expression for True
                            # msg = '{{"pv" : "{pv}",\
                            #         "rule" : "{rule}",\
                            #         "limits" : "{limits}",\
                            #         "phone" : "{phone}"}}'.format(pv=(check1[1])[0] if numpvs==1 else (check1[1])[0]+" and more",\
                            #                                         rule=n.rule1 if numpvs==1 else "Multiple rules",\
                            #                                         limits=n.limits1,\
                            #                                         phone=n.phone)
                            if numpvs == 1:
                                msg = '{{"numpvs" : "{numpvs}",\
                                        "pv1" : "{pv1}",\
                                        "rule1" : "{rule1}",\
                                        "limits1" : "{limits1}",\
                                        "value1" : "{value1}",\
                                        "phone" : "{phone}"}}'.format(numpvs=numpvs,\
                                                                      pv1=(check1[1])[0],\
                                                                      rule1=n.rule1,\
                                                                      limits1=n.limits1,\
                                                                      value1=check1[2][0],\
                                                                      phone=n.phone)
                            elif numpvs == 2:
                                #print("check1[0]:", check1[0], "check2[0]", check2[0])
                                if (check1[0] == True and check2[0] == True):
                                    msg = '{{"numpvs" : "{numpvs}",\
                                            "pv1" : "{pv1}",\
                                            "pv2" : "{pv2}",\
                                            "rule1" : "{rule1}",\
                                            "rule2" : "{rule2}",\
                                            "limits1" : "{limits1}",\
                                            "limits2" : "{limits2}",\
                                            "subrule1" : "{subrule1}",\
                                            "value1" : "{value1}",\
                                            "value2" : "{value2}",\
                                            "phone" : "{phone}"}}'.format(numpvs=numpvs,\
                                                                        pv1=(check1[1])[0],\
                                                                        pv2=(check2[1])[0],\
                                                                        rule1=n.rule1,\
                                                                        rule2=n.rule2,\
                                                                        limits1=n.limits1,\
                                                                        limits2=n.limits2,\
                                                                        subrule1=n.subrule1,\
                                                                        value1=check1[2][0],\
                                                                        value2=check2[2][0],\
                                                                        phone=n.phone)
                                elif (check1[0] == True and check2[0] == False):
                                    msg = '{{"numpvs" : "{numpvs}",\
                                            "pv1" : "{pv1}",\
                                            "pv2" : "{pv2}",\
                                            "rule1" : "{rule1}",\
                                            "rule2" : "{rule2}",\
                                            "limits1" : "{limits1}",\
                                            "limits2" : "{limits2}",\
                                            "subrule1" : "{subrule1}",\
                                            "value1" : "{value1}",\
                                            "value2" : "{value2}",\
                                            "phone" : "{phone}"}}'.format(numpvs=numpvs,\
                                                                        pv1=(check1[1])[0],\
                                                                        pv2=n.pv2,\
                                                                        rule1=n.rule1,\
                                                                        rule2=n.rule2,\
                                                                        limits1=n.limits1,\
                                                                        limits2=n.limits2,\
                                                                        subrule1=n.subrule1,\
                                                                        value1=check1[2][0],\
                                                                        value2="-",\
                                                                        phone=n.phone)
                                elif (check1[0] == False and check2[0] == True):
                                    msg = '{{"numpvs" : "{numpvs}",\
                                            "pv1" : "{pv1}",\
                                            "pv2" : "{pv2}",\
                                            "rule1" : "{rule1}",\
                                            "rule2" : "{rule2}",\
                                            "limits1" : "{limits1}",\
                                            "limits2" : "{limits2}",\
                                            "subrule1" : "{subrule1}",\
                                            "value1" : "{value1}",\
                                            "value2" : "{value2}",\
                                            "phone" : "{phone}"}}'.format(numpvs=numpvs,\
                                                                        pv1=n.pv1,\
                                                                        pv2=(check2[1])[0],\
                                                                        rule1=n.rule1,\
                                                                        rule2=n.rule2,\
                                                                        limits1=n.limits1,\
                                                                        limits2=n.limits2,\
                                                                        subrule1=n.subrule1,\
                                                                        value1="-",\
                                                                        value2=check2[2][0],\
                                                                        phone=n.phone)
                            # elif numpvs == 3:                                           
                            #     msg = '{{"numpvs" : "{numpvs}",\
                            #             "pv1" : "{pv1}",\
                            #             "pv2" : "{pv2}",\
                            #             "pv3" : "{pv3}",\
                            #             "rule1" : "{rule1}",\
                            #             "rule2" : "{rule2}",\
                            #             "rule3" : "{rule3}",\
                            #             "limits1" : "{limits1}",\
                            #             "limits2" : "{limits2}",\
                            #             "limits3" : "{limits3}",\
                            #             "subrule1" : "{subrule1}",\
                            #             "subrule2" : "{subrule2}",\
                            #             "value1" : "{value1}",\
                            #             "value2" : "{value2}",\
                            #             "value3" : "{value3}",\
                            #             "phone" : "{phone}"}}'.format(numpvs=numpvs,\
                            #                                           pv1=(check1[1])[0],\
                            #                                           pv2=(check2[1])[0],\
                            #                                           pv3=(check3[1])[0],\
                            #                                           rule1=n.rule1,\
                            #                                           rule2=n.rule2,\
                            #                                           rule3=n.rule2,\
                            #                                           limits1=n.limits1,\
                            #                                           limits2=n.limits2,\
                            #                                           limits3=n.limits2,\
                            #                                           subrule1=n.subrule1,\
                            #                                           subrule2=n.subrule2,\
                            #                                           value1=check1[2][0],\
                            #                                           value2=check2[2][0],\
                            #                                           value3=check3[2][0],\
                            #                                           phone=n.phone)
                            sent_time = datetime.strptime(n.sent_time, "%Y-%m-%d %H:%M:%S.%f") #- timedelta(hours=3)
                            #print("interval, sent_time, ", n.interval, sent_time)
                            #print("interval, sent_time + delta, ", n.interval, sent_time + timedelta(minutes=int(n.interval)))
                            if (n.sent==False ): #and n.persistent==True) and (now > (sent_time + timedelta(minutes=int(n.interval))))):
                                r = client.client(msg) #send data to Server (modem's PC)
                                #print(msg)
                                #print('client done persistence true')
                                #print('r', r)
                                if r[0]==False:
                                    log = str(datetime.now()) + ' error sending message to server > ' + n.pv1 + '\n\r'
                                    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                    log_path = path.join(dir_path, 'log.txt')
                                    writer.write(log_path, log, 'a')
                                    print(log)
                                else:
                                    log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server > ' + n.pv1 + '\n\r'
                                    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                    log_path = path.join(dir_path, 'log.txt')
                                    writer.write(log_path, log, 'a')
                                    set_sent_db(n.id, True)
                                    set_sent_time_db(n.id, now)
                                    print(log)
                            else:
                                if ((n.persistent==True) and (now > (sent_time + timedelta(minutes=int(n.interval))))):
                                    r = client.client(msg) #send data to Server (modem's PC)
                                    #print(msg)
                                    #print('client done persistence false')
                                    #print('r', r)
                                    if r[0]==False:
                                        log = str(datetime.now()) + ' error sending message to server > ' + n.pv1 + '\n\r'
                                        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                        log_path = path.join(dir_path, 'log.txt')
                                        writer.write(log_path, log, 'a')
                                        print(log)
                                    else:
                                        log = str(datetime.now()) + ' message to owner ' + n.owner + ' sent to server > ' + n.pv1 + '\n\r'
                                        dir_path = path.dirname(path.realpath(__file__)) #current folder application path
                                        log_path = path.join(dir_path, 'log.txt')
                                        writer.write(log_path, log, 'a')
                                        set_sent_db(n.id, True)
                                        set_sent_time_db(n.id, now)
                                        print(log)

            sleep(10)

evaluate()