CREATE TABLE IF NOT EXISTS guilds(
       channel BIGINT PRIMARY KEY,
       guild BIGINT,
       post_amount INT,
       post_frequency INT,
       last_post REAL);

CREATE TABLE IF NOT EXISTS images(
        guild BIGINT,
        image TEXT);