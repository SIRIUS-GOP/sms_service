import sqlite3, os

dir_path = os.path.dirname(os.path.realpath(__file__)) #current folder application path
stripped_path = os.path.dirname(dir_path)
db_path = os.path.join(stripped_path, 'users.db')
connection = sqlite3.connect(db_path)

sql_path = os.path.join(dir_path, 'schema_users.sql')
with open(sql_path) as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users_db (username, password) VALUES (?, ?)",
            ('admin', 'admin')
            )

connection.commit()
connection.close()