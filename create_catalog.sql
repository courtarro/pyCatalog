PRAGMA foreign_keys = true;
CREATE TABLE "music" (
	`item_id`	INTEGER,
	`title`	TEXT,
	`artist`	TEXT,
	`label`	TEXT,
	PRIMARY KEY(item_id),
	FOREIGN KEY(`item_id`) REFERENCES item ( id ) ON DELETE CASCADE
);
CREATE TABLE "movie" (
	`item_id`	INTEGER,
	`title`	TEXT,
	`actor`	TEXT,
	`director`	TEXT,
	`publisher`	TEXT,
	PRIMARY KEY(item_id),
	FOREIGN KEY(`item_id`) REFERENCES item ( id )  ON DELETE CASCADE
);
CREATE TABLE "item" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT
);
CREATE TABLE "image" (
	`item_id`	INTEGER,
	`type`	INTEGER,
	`filename`	TEXT,
	PRIMARY KEY(item_id,type),
	FOREIGN KEY(`item_id`) REFERENCES item ( id )  ON DELETE CASCADE
);
CREATE TABLE "external_id" (
	`item_id`	INTEGER,
	`provider`	INTEGER,
	`external_id`	TEXT,
	PRIMARY KEY(item_id,provider),
	FOREIGN KEY(`item_id`) REFERENCES item ( id )  ON DELETE CASCADE
);
