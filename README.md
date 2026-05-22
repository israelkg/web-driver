# WebDriver - ETL Titanic com Playwright + PostgreSQL

Projeto da disciplina **Ciência de Dados e Mineração de Dados** (3º período).

Pipeline ETL + visualização:
1. **Extract**: Playwright + BeautifulSoup baixam o dataset Titanic do GitHub
2. **Transform**: pandas tipa as colunas e trata nulos
3. **Load**: psycopg2 carrega no PostgreSQL em uma tabela única `passageiros`
4. **Plot**: matplotlib gera 16 gráficos de análise a partir da tabela

Fonte do dataset: https://github.com/datasciencedojo/datasets/blob/master/titanic.csv

> **Nota de modelagem:** o dataset tem só 891 linhas e 12 colunas, então uma tabela única já é suficiente. Star schema (dims + fato) seria overkill aqui — só faria sentido com volume alto, cardinalidade real nas categóricas ou relações M:N.

---

## Estrutura

```
WebDriver/
├── .env                          # credenciais Postgres (criar a partir de .env.example)
├── .env.example                  # template de credenciais
├── .gitignore
├── requirements.txt
├── README.md
├── dados/
│   └── titanic.csv               # gerado pelo extract
├── script-extract/
│   └── task3_titanic.py          # Playwright + BS4 baixa o CSV
├── script-create-database/
│   ├── tables.sql                # DDL: tabela passageiros
│   └── create_database.py        # executa o SQL
├── load-database/
│   └── script-load-database.py   # ETL pandas + COPY
└── script-geracao-grafico/
    ├── script-geracao-grafico.py # gera gráficos via matplotlib
    └── plots/                    # PNGs gerados (16 gráficos)
```

---

## Pré-requisitos

- Python 3.10+
- PostgreSQL rodando localmente
- Banco de dados `titanic` já criado no Postgres
- Git Bash (ou PowerShell, ajustando o caminho do Python)

### Criar o banco no Postgres

No psql, DBeaver ou pgAdmin:

```sql
CREATE DATABASE titanic;
```

---

## Setup (primeira vez)

Dentro da pasta `WebDriver/`, no Git Bash:

```bash
# 1. Copiar template do .env e editar com suas credenciais
cp .env.example .env
# Abra o .env e troque DB_PASS pela sua senha do Postgres

# 2. Criar e ativar o ambiente virtual
python -m venv .venv

# 3. Instalar dependências
.venv/Scripts/python.exe -m pip install -r requirements.txt

# 4. Instalar o navegador do Playwright
.venv/Scripts/python.exe -m playwright install chromium
```

---

## Rodar o pipeline completo

Dentro da pasta `WebDriver/`, no Git Bash:

```bash
# 1. Extract - baixa titanic.csv para dados/
cd script-extract && ../.venv/Scripts/python.exe task3_titanic.py && cd ..

# 2. Create - cria a tabela no banco titanic
cd script-create-database && ../.venv/Scripts/python.exe create_database.py && cd ..

# 3. Load - carrega o CSV no Postgres
cd load-database && ../.venv/Scripts/python.exe script-load-database.py && cd ..

# 4. Plot - gera os gráficos em script-geracao-grafico/plots/
cd script-geracao-grafico && ../.venv/Scripts/python.exe script-geracao-grafico.py && cd ..
```

Ou em uma única linha encadeada (para se um falhar, parar tudo):

```bash
cd script-extract && ../.venv/Scripts/python.exe task3_titanic.py && cd ../script-create-database && ../.venv/Scripts/python.exe create_database.py && cd ../load-database && ../.venv/Scripts/python.exe script-load-database.py && cd ../script-geracao-grafico && ../.venv/Scripts/python.exe script-geracao-grafico.py && cd ..
```

---

## Validar a carga

No psql, DBeaver ou pgAdmin conectado ao banco `titanic`:

```sql
-- Total de passageiros carregados (esperado: 891)
SELECT COUNT(*) FROM passageiros;

-- Sobreviventes (esperado: 549 mortos, 342 sobreviventes)
SELECT survived, COUNT(*) FROM passageiros GROUP BY survived ORDER BY survived;

-- Sobrevivência por classe
SELECT pclass, COUNT(*) AS total, SUM(survived) AS sobreviventes
FROM passageiros GROUP BY pclass ORDER BY pclass;

-- Sobrevivência por porto de embarque
SELECT embarked, COUNT(*) AS total, SUM(survived) AS sobreviventes
FROM passageiros GROUP BY embarked ORDER BY total DESC;

-- Sobrevivência por sexo
SELECT sex, COUNT(*) AS total, SUM(survived) AS sobreviventes
FROM passageiros GROUP BY sex;
```

---

## Esquema da tabela

```
passageiros
├── passenger_id  INT PK
├── survived      INT       (0 = não, 1 = sim)
├── pclass        INT       (1, 2 ou 3 - classe da passagem)
├── name          VARCHAR
├── sex           VARCHAR
├── age           FLOAT
├── sibsp         INT       (irmãos/cônjuges a bordo)
├── parch         INT       (pais/filhos a bordo)
├── ticket        VARCHAR
├── fare          FLOAT
├── cabin         VARCHAR
└── embarked      CHAR(1)   (S=Southampton, C=Cherbourg, Q=Queenstown)
```

---

## Re-executar a carga

`tables.sql` é idempotente (faz `DROP TABLE IF EXISTS` antes de criar). Pode rodar `create_database.py` quantas vezes quiser sem dar erro.

`script-load-database.py` faz `TRUNCATE` antes de carregar, então também é seguro rodar várias vezes.

`script-geracao-grafico.py` sobrescreve os PNGs em `plots/` a cada execução. Roda sozinho desde que a tabela `passageiros` esteja populada.

---

## Problemas comuns

**`psycopg2.OperationalError: could not connect`**
Postgres não está rodando ou as credenciais no `.env` estão erradas.

**`database "titanic" does not exist`**
Crie o banco antes: `CREATE DATABASE titanic;`

**`playwright._impl._errors.Error: Executable doesn't exist`**
Falta o navegador. Rode: `.venv/Scripts/python.exe -m playwright install chromium`

**`ModuleNotFoundError: No module named 'pandas'` (ou outro)**
Esqueceu de ativar o venv ou de instalar os requirements.

**Falha ao compilar pandas (Python 3.14)**
Pandas mais antigo não tem wheel pra Python 3.14. Os `requirements.txt` usam `>=` justamente pra pegar versões recentes. Se ainda assim falhar, use Python 3.12.
