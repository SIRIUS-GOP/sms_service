import sqlite3
from os import path
import re

def get_notifications_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/notifications.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_rules_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/rules.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_users_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/users.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_fullpvlist_connection():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/fullpvlist.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_fullpvlist_conn():
    dir_path = path.dirname(path.realpath(__file__)) #current folder application path
    db_path = path.join(dir_path, 'db/fullpvlist.db')
    conn = sqlite3.connect(db_path)
    return conn
    
def get_rule(rule_id):
    conn = get_rules_connection()
    rule = conn.execute('SELECT * FROM rules_db WHERE id = ?',
                    (rule_id,)).fetchone()
    conn.close()
    return rule

def get_notification(notification_id):
    conn = get_notifications_connection()
    notification = conn.execute('SELECT * FROM notifications_db WHERE id = ?',
                    (notification_id,)).fetchone()
    conn.close()
    return notification

def get_notification_id(notifications_id):
    conn = get_notifications_connection()
    notifications = conn.execute('SELECT * FROM notifications_db WHERE id = ?',
                    (notifications_id,)).fetchone()
    conn.close()
    return notifications

def rules_math(notifications_id):
    conn = get_notifications_connection()
    notifications = conn.execute('SELECT * FROM notifications_db WHERE id = ?',
                    (notifications_id,)).fetchone()
    conn.close()
    return notifications

def get_notifications_db():
    conn = get_notifications_connection()
    notifications = conn.execute('SELECT * FROM notifications_db').fetchall()
    return notifications

def set_sent_db(id, val):
    conn = get_notifications_connection()
    conn.execute('UPDATE notifications_db SET sent = ?'
                    ' WHERE id = ?',
                    (val, id))
    conn.commit()

def set_sent_time_db(id, val):
    conn = get_notifications_connection()
    conn.execute('UPDATE notifications_db SET sent_time = ?'
                    ' WHERE id = ?',
                    (val, id))
    conn.commit()

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
