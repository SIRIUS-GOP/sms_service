import sqlite3
from os import path

def get_notifications_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/notifications.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_notifications_old_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/notifications_old.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def run():
    old = get_notifications_old_connection()
    rows_old = old.execute("SELECT * FROM notifications_db").fetchall()
    new = get_notifications_connection()
    rows_new = new.execute("SELECT * FROM notifications_db").fetchall()
    i = 0
    for row in rows_old:
        j = 0
        for row in rows_old[i]:
            # print(row)
            if j==0:
                id = rows_old[i][j]
            if j==1:
                created = rows_old[i][j]
            if j==2:
                expiration = rows_old[i][j]
            if j==3:
                owner = rows_old[i][j]
            if j==4:
                phone = rows_old[i][j]
            if j==5:
                pv1 = rows_old[i][j]
            if j==6:
                rule1 = rows_old[i][j]
            if j==7:
                limits1 = rows_old[i][j]
            if j==8:
                subrule1 = rows_old[i][j]
            if j==9:
                pv2 = rows_old[i][j]
            if j==10:
                rule2 = rows_old[i][j]
            if j==11:
                limits2 = rows_old[i][j]
            if j==12:
                subrule2 = rows_old[i][j]
            if j==13:
                pv3 = rows_old[i][j]
            if j==14:
                rule3 = rows_old[i][j]
            if j==15:
                limits3 = rows_old[i][j]
            if j==16:
                sent = rows_old[i][j]
            if j==17:
                sent_time = rows_old[i][j]
            if j==18:
                interval = rows_old[i][j]
            if j==19:
                persistent = rows_old[i][j]
            print(j, end=" ", flush=True)
            j += 1
        # print(id)
        # print(created)
        # print(expiration)
        # print(pv)
        # print(rule)
        # print(limits)
        # print(owner)
        # print(phone)
        # print(sent)
        # print(sent_time)
        # print(interval)
        # print(persistent)
        # print("i", i, "j", j)
        new.execute('INSERT INTO notifications_db (id, created, expiration, owner, phone, \
            pv1, rule1, limits1, subrule1, pv2, rule2, limits2, subrule2, pv3, rule3, limits3, \
            sent, sent_time, interval, persistent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
            ?, ?, ?, ?, ?, ?, ?, ?)',
            (id, created, expiration, owner, phone, pv1, rule1, limits1, subrule1, pv2, rule2, 
            limits2, subrule2, pv3, rule3, limits3, sent, sent_time, interval, persistent))
        print(" - row %i done" % i)
        i += 1

    new.commit()
    new.close()
    old.close()
    #print(len(list(rows_old[0])))

run()