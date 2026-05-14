# WebDriver - ETL Titanic com Playwright + PostgreSQL

Projeto da disciplina **Ciência de Dados e Mineração de Dados** (3º período).

Pipeline ETL completo:
1. **Extract**: Playwright + BeautifulSoup baixam o dataset Titanic do GitHub
2. **Transform**: pandas tipa as colunas e trata nulos
3. **Load**: psycopg2 carrega no PostgreSQL usando esquema estrela

Fonte do dataset: https://github.com/datasciencedojo/datasets/blob/master/titanic.csv

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
│   ├── tables.sql                # DDL: dim_classe, dim_embarque, fato_passageiro
│   └── create_database.py        # executa o SQL
└── load-database/
    └── script-load-database.py   # ETL pandas + COPY
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

# 2. Create - cria as tabelas no banco titanic
cd script-create-database && ../.venv/Scripts/python.exe create_database.py && cd ..

# 3. Load - carrega o CSV no Postgres
cd load-database && ../.venv/Scripts/python.exe script-load-database.py && cd ..
```

Ou em uma única linha encadeada (para se um falhar, parar tudo):

```bash
cd script-extract && ../.venv/Scripts/python.exe task3_titanic.py && cd ../script-create-database && ../.venv/Scripts/python.exe create_database.py && cd ../load-database && ../.venv/Scripts/python.exe script-load-database.py && cd ..
```

---

## Validar a carga

No psql, DBeaver ou pgAdmin conectado ao banco `titanic`:

```sql
-- Total de passageiros carregados (esperado: 891)
SELECT COUNT(*) FROM fato_passageiro;

-- Sobreviventes (esperado: 549 mortos, 342 sobreviventes)
SELECT survived, COUNT(*) FROM fato_passageiro GROUP BY survived ORDER BY survived;

-- Sobrevivência por classe
SELECT c.descricao, COUNT(*) AS total, SUM(survived) AS sobreviventes
FROM fato_passageiro f JOIN dim_classe c USING (id_classe)
GROUP BY c.descricao ORDER BY total DESC;

-- Sobrevivência por porto de embarque
SELECT e.porto, COUNT(*) AS total, SUM(survived) AS sobreviventes
FROM fato_passageiro f JOIN dim_embarque e USING (id_embarque)
GROUP BY e.porto ORDER BY total DESC;
```

---

## Modelo dimensional

```
dim_classe                   dim_embarque
┌─────────────┐              ┌──────────────┐
│ id_classe   │              │ id_embarque  │
│ pclass      │              │ embarked     │
│ descricao   │              │ porto        │
└──────┬──────┘              └──────┬───────┘
       │                             │
       │       fato_passageiro       │
       │      ┌──────────────────┐   │
       └─────►│ id_classe        │◄──┘
              │ id_embarque      │
              │ passenger_id     │
              │ survived         │
              │ name, sex, age   │
              │ sibsp, parch     │
              │ ticket, fare     │
              │ cabin            │
              └──────────────────┘
```

---

## Re-executar a carga

`tables.sql` é idempotente (faz `DROP TABLE IF EXISTS` antes de criar). Pode rodar `create_database.py` quantas vezes quiser sem dar erro.

`script-load-database.py` faz `TRUNCATE` na fato antes de carregar, então também é seguro rodar várias vezes.

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
