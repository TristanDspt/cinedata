-- schema.sql

CREATE TABLE IF NOT EXISTS movies (
    id                INTEGER PRIMARY KEY,
    title             TEXT,
    tagline           TEXT,
    director          TEXT,
    casting           TEXT,
    release_date      TEXT,
    duration          INTEGER,
    budget            REAL,
    revenue           REAL,
    genres            TEXT,
    synopsis          TEXT,
    vote_average_tmdb REAL,
    vote_count_tmdb   INTEGER,
    vote_average_ml   REAL,
    vote_count_ml     INTEGER
);