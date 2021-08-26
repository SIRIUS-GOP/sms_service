DROP TABLE IF EXISTS rules_db;

CREATE TABLE rules_db (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule TEXT NOT NULL,
    description TEXT NOT NULL,
    owner TEXT NOT NULL
);