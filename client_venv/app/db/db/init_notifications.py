import sqlite3, os

dir_path = os.path.dirname(os.path.realpath(__file__)) #current folder application path
stripped_path = os.path.dirname(dir_path)
db_path = os.path.join(stripped_path, 'notifications.db')
connection = sqlite3.connect(db_path)

sql_path = os.path.join(dir_path, 'schema_notifications.sql')
with open(sql_path) as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO notifications_db (pv, rule, limits, owner, phone) VALUES (?, ?, ?, ?, ?)",
            ('SI-13C4:DI-DCCT:Current-Mon', 'pv < L', 'L=0', 'rone.castro', '(XX)12345-6789')
            )

connection.commit()
connection.close()