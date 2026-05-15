import os
import io
import time
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv('../.env')


def bulk_copy_to_db(cursor, df, table_name, columns):
    df_to_copy = df[columns].copy()
    buffer = io.StringIO()
    df_to_copy.to_csv(buffer, index=False, header=False, sep=';', na_rep='\\N')
    buffer.seek(0)

    sql = f"COPY {table_name} ({','.join(columns)}) FROM STDIN WITH CSV DELIMITER ';' NULL '\\N'"
    cursor.copy_expert(sql, buffer)


def tipar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"passengerid": "passenger_id"})

    colunas_int = ['passenger_id', 'survived', 'pclass', 'sibsp', 'parch']
    colunas_float = ['age', 'fare']
    colunas_string = ['name', 'sex', 'ticket', 'cabin', 'embarked']

    for col in colunas_int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    for col in colunas_float:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Float64')
    for col in colunas_string:
        if col in df.columns:
            df[col] = df[col].astype('string').str.strip()
            df.loc[df[col] == '', col] = pd.NA
    return df


def executar_etl_completo(caminho_csv):
    conn_params = {
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "port": os.getenv("DB_PORT"),
    }

    conn = None
    try:
        print("Lendo e tipando CSV...")
        df = pd.read_csv(caminho_csv, sep=',', encoding='utf-8')
        df = tipar_dataframe(df)

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        start_total = time.time()

        cur.execute("TRUNCATE TABLE passageiros")

        colunas = [
            'passenger_id', 'survived', 'pclass', 'name', 'sex',
            'age', 'sibsp', 'parch', 'ticket', 'fare', 'cabin', 'embarked'
        ]

        print(f"Inserindo {len(df)} passageiros...")
        bulk_copy_to_db(cur, df, 'passageiros', colunas)

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM passageiros")
        total = cur.fetchone()[0]
        cur.execute("SELECT survived, COUNT(*) FROM passageiros GROUP BY survived ORDER BY survived")
        sobrev = cur.fetchall()

        print(f"ETL finalizado em {time.time() - start_total:.2f}s")
        print(f"Total em passageiros: {total}")
        print(f"Sobreviventes (0=nao, 1=sim): {sobrev}")

    except Exception as e:
        print(f"Erro no ETL: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    executar_etl_completo('../dados/titanic.csv')
