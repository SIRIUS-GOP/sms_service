DROP TABLE IF EXISTS notifications_db;

CREATE TABLE notifications_db (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    expiration TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
    pv TEXT NOT NULL,
    rule INTEGER NOT NULL,
    limits TEXT NOT NULL,
    owner TEXT NOT NULL,
    phone TEXT NOT NULL,
    sent BOOLEAN NOT NULL DEFAULT 0,
    sent_time DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'now', 'localtime')),
    interval integer NOT NULL DEFAULT 10,
    persistent BOOLEAN NOT NULL DEFAULT 0
);