CREATE TABLE IF NOT EXISTS users (
    ID INTEGER NOT NULL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
   	password TEXT NOT NULL UNIQUE
   	    CHECK (length(password) >= 6),
   	ability TEXT,
   	phone TEXT NOT NULL
   	    CHECK (length(phone) == 11)
);

