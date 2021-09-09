DROP TABLE IF EXISTS notifications_db;

CREATE TABLE notifications_db (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    expiration TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    owner TEXT NOT NULL,
    phone TEXT NOT NULL,
    pv1 TEXT NOT NULL,
    rule1 INTEGER NOT NULL,
    limits1 TEXT NOT NULL,
    subrule1 TEXT,
    pv2 TEXT,
    rule2 INTEGER,
    limits2 TEXT,
    subrule2 TEXT,
    pv3 TEXT,
    rule3 INTEGER,
    limits3 TEXT,
    sent BOOLEAN NOT NULL DEFAULT 0,
    sent_time DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')),
    interval integer NOT NULL DEFAULT 10,
    persistent BOOLEAN NOT NULL DEFAULT 0
);