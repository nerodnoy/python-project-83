DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS url_checks;

CREATE TABLE url_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id BIGINT REFERENCES urls (id),
    status_code BIGINT,
    h1 text,
    title text,
    description text,
    created_at TIMESTAMP NOT NULL
);