DROP KEYSPACE IF EXISTS market;

CREATE KEYSPACE market WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE market;

CREATE TABLE trades(
    uuid uuid,
    trade_conditions text,
    price double,
    symbol text,
    trade_ts timestamp,
    ingestion_ts timestamp,
    volume double,
    type text,
    PRIMARY KEY ( (symbol), trade_ts )
);

CREATE INDEX IF NOT EXISTS ON trades (uuid);

CREATE TABLE run_10_s_avg(
    uuid uuid,
    symbol text,
    price_x_volume double,
    ingestion_ts timestamp,
    PRIMARY KEY ( (uuid), ingestion_ts )
);

CREATE INDEX IF NOT EXISTS ON run_10_s_avg (symbol);