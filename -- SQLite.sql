-- SQLite
CREATE TABLE ingredientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    unidad TEXT,
    cantidad REAL DEFAULT 0.0
);