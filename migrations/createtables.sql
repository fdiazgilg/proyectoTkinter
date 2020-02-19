BEGIN TRANSACTION;

DROP TABLE IF EXISTS cryptos;

CREATE TABLE "cryptos" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"symbol"	TEXT NOT NULL,
	"name"	TEXT NOT NULL
);


DROP TABLE IF EXISTS movements;

CREATE TABLE "movements" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"date"	TEXT NOT NULL,
	"time"	TEXT NOT NULL,
	"from_currency"	INTEGER NOT NULL,
	"from_quantity"	REAL,
	"to_currency"	INTEGER NOT NULL,
	"to_quantity"	REAL,
	FOREIGN KEY("to_currency") REFERENCES "cryptos"("id"),
	FOREIGN KEY("from_currency") REFERENCES "cryptos"("id")
);


DROP VIEW IF EXISTS moves;

CREATE VIEW moves AS SELECT 
	b.date, 
	b.time, 
	a.name, 
	b.from_quantity, 
	c.name, 
	b.to_quantity 
	FROM cryptos a INNER JOIN(cryptos c INNER JOIN movements b ON c.id = b.to_currency) 
	ON a.id = b.from_currency 
	ORDER BY b.id;


COMMIT;