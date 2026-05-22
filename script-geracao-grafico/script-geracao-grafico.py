import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv('../.env')

DB = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
}

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def save(filename):
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=150)
    plt.close()


conn = psycopg2.connect(**DB)
df = pd.read_sql('SELECT * FROM passageiros', conn)
conn.close()

df = df.rename(columns={
    'sex': 'Sex',
    'pclass': 'Pclass',
    'survived': 'Survived',
    'age': 'Age',
})

CLASSES = {1: "Primeira Classe", 2: "Segunda Classe", 3: "Terceira Classe"}
SEX_LABEL = {'female': 'Mulher', 'male': 'Homem'}

contagem_sex = df['Sex'].value_counts().sort_index()
contagem_sex.plot(kind='bar', color=['pink', 'blue'], figsize=(10, 6))
plt.title('Distribuição de Gênero no Titanic', fontsize=16)
plt.xlabel('Gênero', fontsize=12)
plt.ylabel('Contagem', fontsize=12)
plt.xticks(ticks=range(len(contagem_sex)),
           labels=[SEX_LABEL[s] for s in contagem_sex.index], rotation=0, fontsize=12)
plt.yticks(fontsize=12)
save("01_distribuicao_genero.png")

contagem_por_classe_e_genero = df.groupby(['Pclass', 'Sex']).size().unstack()
contagem_por_classe_e_genero.plot(kind='bar', stacked=True, figsize=(10, 6), color=['lightpink', 'skyblue'])
plt.title('Distribuição de Gênero por Classe no Titanic', fontsize=16)
plt.xlabel('Classe de Passageiro', fontsize=14)
plt.ylabel('Quantidade', fontsize=14)
plt.xticks(ticks=range(3), labels=list(CLASSES.values()), rotation=0, fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title='Gênero', fontsize=12, title_fontsize='13')
save("02_genero_por_classe.png")

contagem_sobrev_genero = df.groupby(['Sex', 'Survived']).size().unstack()
contagem_sobrev_genero.plot(kind='bar', stacked=False, figsize=(10, 6), color=['#d9534f', '#5cb85c'])
plt.title('Quantidade de Sobreviventes por Gênero no Titanic', fontsize=16)
plt.xlabel('Gênero', fontsize=14)
plt.ylabel('Quantidade', fontsize=14)
plt.xticks(ticks=range(len(contagem_sobrev_genero)),
           labels=[SEX_LABEL[s] for s in contagem_sobrev_genero.index], rotation=0, fontsize=12)
plt.legend(['Não Sobreviveu', 'Sobreviveu'], title='Status', fontsize=12)
save("03_sobreviventes_por_genero_geral.png")

contagem_por_classe_genero = df.groupby(['Pclass', 'Sex']).size().unstack()
contagem_por_classe_sobrev  = df.groupby(['Pclass', 'Survived']).size().unstack()

for pclass, nome in CLASSES.items():
    slug = nome.lower().replace(" ", "_")

    dados_classe = df[df['Pclass'] == pclass]
    sobrev = dados_classe.groupby(['Sex', 'Survived']).size().unstack()
    sobrev.plot(kind='bar', stacked=False, figsize=(10, 6), color=['#d9534f', '#5cb85c'])
    plt.title(f'Sobreviventes por Gênero — {nome}', fontsize=16)
    plt.xlabel('Gênero', fontsize=14)
    plt.ylabel('Quantidade', fontsize=14)
    plt.xticks(ticks=range(len(sobrev)),
               labels=[SEX_LABEL[s] for s in sobrev.index], rotation=0, fontsize=12)
    plt.legend(['Não Sobreviveu', 'Sobreviveu'], title='Status', fontsize=12, loc='upper right')
    save(f"04_sobreviventes_genero_{slug}.png")

    dados_genero = contagem_por_classe_genero.loc[pclass]
    fig, ax = plt.subplots()
    ax.pie(dados_genero, labels=[SEX_LABEL[s] for s in dados_genero.index],
           colors=['lightpink', 'skyblue'], startangle=90, autopct='%1.1f%%',
           wedgeprops=dict(width=0.3))
    plt.title(f'Distribuição de Gênero — {nome}', fontsize=16)
    save(f"05_rosca_genero_{slug}.png")

    dados_sobrev = contagem_por_classe_sobrev.loc[pclass]
    fig, ax = plt.subplots()
    ax.pie(dados_sobrev, labels=['Não Sobreviveu', 'Sobreviveu'],
           colors=['#d9534f', '#5cb85c'], startangle=90, autopct='%1.1f%%',
           wedgeprops=dict(width=0.3))
    plt.title(f'Sobrevivência — {nome}', fontsize=16)
    save(f"06_rosca_sobrevivencia_{slug}.png")

bins   = [0, 10, 20, 30, 40, 50, 60, 70, 80]
labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80']
df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels)
age_group_survival = df.groupby(['AgeGroup', 'Survived'], observed=True).size().unstack(fill_value=0)
age_group_survival.plot(kind='barh', stacked=True, figsize=(10, 6))
plt.xlabel('Número de Passageiros')
plt.ylabel('Faixa Etária')
plt.title('Sobrevivência por Faixa Etária no Titanic')
plt.legend(['Não Sobreviveu', 'Sobreviveu'], title='Sobreviveu')
save("07_sobrevivencia_faixa_etaria_geral.png")

for pclass, nome in CLASSES.items():
    slug = nome.lower().replace(" ", "_")
    dados_classe = df[df['Pclass'] == pclass].copy()
    dados_classe['AgeGroup'] = pd.cut(dados_classe['Age'], bins=bins, labels=labels)
    age_surv = dados_classe.groupby(['AgeGroup', 'Survived'], observed=True).size().unstack(fill_value=0)
    age_surv.plot(kind='barh', stacked=True, figsize=(10, 6))
    plt.xlabel('Número de Passageiros')
    plt.ylabel('Faixa Etária')
    plt.title(f'Sobrevivência por Faixa Etária — {nome}')
    plt.legend(['Não Sobreviveu', 'Sobreviveu'], title='Sobreviveu')
    save(f"08_sobrevivencia_faixa_etaria_{slug}.png")

print(f"Plots salvos em: {PLOTS_DIR}")
