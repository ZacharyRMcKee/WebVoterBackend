CREATE TABLE queryLink(
	url VARCHAR,
	query VARCHAR,
	rating INTEGER,
	PRIMARY KEY (url,query)
);
CREATE TABLE queryLink_user(
	url VARCHAR,
	query VARCHAR,
	userID INTEGER,
	vote INTEGER,
	PRIMARY KEY (url,query,userID),
	FOREIGN KEY (url,query) REFERENCES queryLink (url,query) ON UPDATE CASCADE
);
