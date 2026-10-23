BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "categorias" (
	"id"	INTEGER,
	"nombre"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "detalle_pedido" (
	"id"	INTEGER,
	"pedido_id"	INTEGER,
	"producto_id"	INTEGER,
	"cantidad"	INTEGER NOT NULL,
	"precio_unitario"	REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("pedido_id") REFERENCES "pedidos"("id"),
	FOREIGN KEY("producto_id") REFERENCES "productos"("id")
);
CREATE TABLE IF NOT EXISTS "pedidos" (
	"id"	INTEGER,
	"usuario_id"	INTEGER,
	"total"	REAL NOT NULL,
	"estado"	TEXT DEFAULT 'pendiente',
	"fecha_pedido"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("usuario_id") REFERENCES "usuarios"("id")
);
CREATE TABLE IF NOT EXISTS "productos" (
	"id"	INTEGER,
	"categoria_id"	INTEGER,
	"nombre"	TEXT NOT NULL,
	"descripcion"	TEXT,
	"precio"	REAL NOT NULL,
	"talla"	TEXT NOT NULL,
	"color"	TEXT NOT NULL,
	"stock"	INTEGER NOT NULL,
	"imagen"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("categoria_id") REFERENCES "categorias"("id")
);
CREATE TABLE IF NOT EXISTS "usuarios" (
	"id"	INTEGER,
	"nombre"	TEXT NOT NULL,
	"email"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"direccion"	TEXT,
	"creado_en"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
