--SQLite
-- CREATE TABLE ingredientes (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     nombre TEXT NOT NULL UNIQUE,
--     unidad TEXT,
--     cantidad INTEGER DEFAULT 0
-- );

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    rut TEXT UNIQUE, 
    telefono TEXT,
    correo TEXT UNIQUE
);

-- CREATE TABLE menus (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     nombre TEXT NOT NULL UNIQUE,
--     precio REAL NOT NULL,
--     categoria TEXT 
-- );
--DROP TABLE IF EXISTS clientes;

-- CREATE TABLE pedidos (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     cliente_id INTEGER, 
--     fecha DATETIME,     
--     total REAL,
--     FOREIGN KEY(cliente_id) REFERENCES clientes(id)
-- );
-- CREATE TABLE menu_ingredientes (
--     menu_id INTEGER,
--     ingrediente_id INTEGER,
--     cantidad_necesaria INTEGER NOT NULL DEFAULT 1,
--     FOREIGN KEY(menu_id) REFERENCES menus(id) ON DELETE CASCADE,
--     FOREIGN KEY(ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
--     PRIMARY KEY (menu_id, ingrediente_id)
-- );