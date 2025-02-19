INIT_QUERY = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "ingredients" (
	"id"	NUMERIC NOT NULL UNIQUE,
	"name"	TEXT NOT NULL COLLATE NOCASE,
	"description"	TEXT,
	"type"	TEXT COLLATE NOCASE,
	"alcohol"	BOOLEAN NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "ingredient_inventory" (
	"user_id"	NUMERIC,
	"ingredient_id"	NUMERIC,
	"amount"	REAL NOT NULL,
	"modified"	DATETIME NOT NULL,
	FOREIGN KEY("ingredient_id") REFERENCES "ingredients"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	UNIQUE("user_id","ingredient_id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	NUMERIC NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"created"	DATETIME NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "drink_inventory" (
	"user_id"	NUMERIC,
	"drink_id"	NUMERIC,
	"amount"	REAL NOT NULL,
	"modified"	DATETIME NOT NULL,
	FOREIGN KEY("drink_id") REFERENCES "drinks"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	UNIQUE("user_id","drink_id")
);
CREATE TABLE IF NOT EXISTS "drink_ingredients" (
	"drink_id"	NUMERIC NOT NULL,
	"ingredient_id"	NUMERIC NOT NULL,
	"measure"	TEXT,
	FOREIGN KEY("drink_id") REFERENCES "drinks"("id"),
	FOREIGN KEY("ingredient_id") REFERENCES "ingredients"("id")
);
CREATE TABLE IF NOT EXISTS "drinks" (
	"id"	NUMERIC NOT NULL UNIQUE,
	"name"	TEXT NOT NULL COLLATE NOCASE,
	"name_alternate"	TEXT COLLATE NOCASE,
	"tags"	TEXT,
	"category"	TEXT COLLATE NOCASE,
	"alcoholic"	BOOLEAN NOT NULL,
	"glass"	NUMERIC NOT NULL COLLATE NOCASE,
	"instructions"	TEXT,
	"thumbnail"	TEXT,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "glass_inventory" (
	"user_id"	NUMERIC NOT NULL,
	"glass_id"	NUMERIC NOT NULL,
	"amount"	INTEGER NOT NULL,
	"modified"	DATETIME NOT NULL,
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	FOREIGN KEY("glass_id") REFERENCES "glasses"("id"),
	UNIQUE("user_id","glass_id")
);
CREATE TABLE IF NOT EXISTS "glasses" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL COLLATE NOCASE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
"""
