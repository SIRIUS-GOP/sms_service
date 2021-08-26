import sqlite3, os

dir_path = os.path.dirname(os.path.realpath(__file__)) #current folder application path
stripped_path = os.path.dirname(dir_path)
db_path = os.path.join(stripped_path, 'notifications_sub.db')
connection = sqlite3.connect(db_path)

sql_path = os.path.join(dir_path, 'schema_notifications_sub.sql')
with open(sql_path) as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO notifications_sub_db (pv, rule, limits, linked_id) VALUES (?, ?, ?, ?)",
            ('AS-Glob:AP-MachShift:Mode-Sts', 'pv = L', 'L=0', '1')
            )

connection.commit()
connection.close()