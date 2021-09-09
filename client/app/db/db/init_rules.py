import sqlite3, os

dir_path = os.path.dirname(os.path.realpath(__file__)) #current folder application path
stripped_path = os.path.dirname(dir_path)
db_path = os.path.join(stripped_path, 'rules.db')
connection = sqlite3.connect(db_path)

sql_path = os.path.join(dir_path, 'schema_rules.sql')
with open(sql_path) as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv == L', 'PV value is equal to Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv != L', 'PV value is different from Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv > L', 'PV value is greater than Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv < L', 'PV value is less than Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv >= L', 'PV value is greater than or equal to Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('pv <= L', 'PV value is less than or equal to Limit', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('(pv < LL) and (pv > LU)', 'PV value is outside range', 'admin')
            )

cur.execute("INSERT INTO rules_db (rule, description, owner) VALUES (?, ?, ?)",
            ('(pv > LL) and (pv < LU)', 'PV value is within range', 'admin')
            )

connection.commit()
connection.close()