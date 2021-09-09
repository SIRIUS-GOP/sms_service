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
                pv = rows_old[i][j]
            if j==4:
                rule = rows_old[i][j]
            if j==5:
                limits = rows_old[i][j]
            if j==6:
                owner = rows_old[i][j]
            if j==7:
                phone = rows_old[i][j]
            if j==8:
                sent = rows_old[i][j]
            if j==9:
                sent_time = rows_old[i][j]
            if j==10:
                interval = rows_old[i][j]
            if j==11:
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
        new.execute('INSERT INTO notifications_db (id, created, expiration, pv, rule, limits, owner, \
            phone, sent, sent_time, interval, persistent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (id, created, expiration, pv, rule, limits, owner, phone, sent, sent_time, interval, persistent))
        print(" - row %i done" % i)
        i += 1

    new.commit()
    new.close()
    old.close()
    #print(len(list(rows_old[0])))

run()