-- Limpeza idempotente (permite re-rodar o script)
DROP TABLE IF EXISTS fato_passageiro CASCADE;
DROP TABLE IF EXISTS dim_classe CASCADE;
DROP TABLE IF EXISTS dim_embarque CASCADE;

-- 1. Dimensões
CREATE TABLE dim_classe (
    id_classe SERIAL PRIMARY KEY,
    pclass INT UNIQUE,
    descricao VARCHAR(20)
);

CREATE TABLE dim_embarque (
    id_embarque SERIAL PRIMARY KEY,
    embarked CHAR(1) UNIQUE,
    porto VARCHAR(20)
);

-- 2. Fato
CREATE TABLE fato_passageiro (
    id_fato SERIAL PRIMARY KEY,
    passenger_id INT UNIQUE,
    survived INT,
    id_classe INT REFERENCES dim_classe(id_classe),
    name VARCHAR(120),
    sex VARCHAR(10),
    age FLOAT,
    sibsp INT,
    parch INT,
    ticket VARCHAR(30),
    fare FLOAT,
    cabin VARCHAR(30),
    id_embarque INT REFERENCES dim_embarque(id_embarque)
);

-- 3. Seed das dimensões (valores fixos do dataset)
INSERT INTO dim_classe (pclass, descricao) VALUES
    (1, 'Primeira'),
    (2, 'Segunda'),
    (3, 'Terceira');

INSERT INTO dim_embarque (embarked, porto) VALUES
    ('S', 'Southampton'),
    ('C', 'Cherbourg'),
    ('Q', 'Queenstown');
