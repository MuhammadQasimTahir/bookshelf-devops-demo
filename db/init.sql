-- Schema + seed data. Runs automatically the FIRST time the MySQL volume is created
-- (docker-entrypoint-initdb.d), and is imported by the CI test job.

CREATE TABLE IF NOT EXISTS books (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    author     VARCHAR(120) NOT NULL,
    year       SMALLINT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO books (title, author, year) VALUES
    ('The Phoenix Project', 'Gene Kim', 2013),
    ('The DevOps Handbook', 'Gene Kim', 2016),
    ('Accelerate', 'Nicole Forsgren', 2018),
    ('Site Reliability Engineering', 'Betsy Beyer', 2016),
    ('Continuous Delivery', 'Jez Humble', 2010);
