-- Limpeza idempotente (permite re-rodar o script)
DROP TABLE IF EXISTS passageiros CASCADE;

CREATE TABLE passageiros (
    passenger_id INT PRIMARY KEY,
    survived INT,
    pclass INT,
    name VARCHAR(120),
    sex VARCHAR(10),
    age FLOAT,
    sibsp INT,
    parch INT,
    ticket VARCHAR(30),
    fare FLOAT,
    cabin VARCHAR(30),
    embarked CHAR(1)
);
