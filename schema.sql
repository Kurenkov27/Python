DROP TABLE IF EXISTS author;

CREATE TABLE exchange (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_to TEXT NOT NULL,
    exchange_rate FLOAT NOT NULL,
    amount FLOAT NOT NULL,
    result FLOAT NOT NULL
);


