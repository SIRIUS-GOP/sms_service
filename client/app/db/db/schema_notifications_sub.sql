DROP TABLE IF EXISTS notifications_sub_db;

CREATE TABLE notifications_sub_db (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pv TEXT NOT NULL,
    rule INTEGER NOT NULL,
    limits TEXT NOT NULL,
    linked_id INTEGER NOT NULL
);