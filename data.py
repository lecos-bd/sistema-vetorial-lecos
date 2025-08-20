import pandas as pd
import numpy as np
from collections import defaultdict
import os
import json

# Ler o arquivo Excel
df = pd.read_excel('Planilha Geral - Índice Trilema Brasil -  Atualizada - (2018-2024) - 0.1.xlsx', sheet_name='Trilema energético')

# ---------------------- Funções de tratamenro ---------------------- #

# Derreter os dados filtrados para Equidade, Segurança e Ambiental
def tratamento_equidade():
    df_equidade = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Equidade 2018', 'Equidade 2019', 'Equidade 2020', 'Equidade 2021', 'Equidade 2022', 'Equidade 2023', 'Equidade 2024'],
        var_name='Dimensão',
        value_name='Escala'
    )
    df_equidade['Ano'] = df_equidade['Dimensão'].str.slice(-4)
    return df_equidade

def tratamento_seguranca():
    df_seguranca = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Segurança 2018', 'Segurança 2019', 'Segurança 2020', 'Segurança 2021', 'Segurança 2022', 'Segurança 2023','Segurança 2024'],
        var_name='Dimensão',
        value_name='Escala'
    )
    df_seguranca['Ano'] = df_seguranca['Dimensão'].str.slice(-4)

    return df_seguranca

def tratamento_ambiental():
    df_ambiental = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Ambiental 2018', 'Ambiental 2019', 'Ambiental 2020', 'Ambiental 2021', 'Ambiental 2022','Ambiental 2023', 'Ambiental 2024'],
        var_name='Dimensão',
        value_name='Escala'
    )
    df_ambiental['Ano'] = df_ambiental['Dimensão'].str.slice(-4)
    return df_ambiental


def capturar_ano():
    df_ambiental = tratamento_ambiental()
    ano = df_ambiental['Ano'].unique()
    return ano

def capturar_estado():
    df_ambiental = tratamento_ambiental()
    estado = df_ambiental['Estado'].unique()
    return estado

# ---------------------- Funções específicas ---------------------- #

# Função manual de truncamento de casas decimais
def truncar(series, casas=4):
    fator = 10 ** casas
    return np.trunc(series * fator) / fator

# Compara as colunas de trilema e retornar os valores comuns e um df com os resultados
def comparar_trilemas(df, ano1, ano2, casas=4):
    df_local = df.copy()

    # Truncar colunas especificadas
    df_local[ano1] = truncar(df_local[ano1], casas)
    df_local[ano2] = truncar(df_local[ano2], casas)

    # Valores únicos de cada ano
    set1 = set(df_local[ano1].unique())
    set2 = set(df_local[ano2].unique())

    # Interseção de valores
    valores_comuns = sorted(set1 & set2)

    # DataFrames com os estados que têm esses valores
    df_ano1 = df_local[df_local[ano1].isin(valores_comuns)][['Estado', ano1]].rename(columns={ano1: 'Valor'})
    df_ano1['Ano'] = ano1

    df_ano2 = df_local[df_local[ano2].isin(valores_comuns)][['Estado', ano2]].rename(columns={ano2: 'Valor'})
    df_ano2['Ano'] = ano2

    # Junta os dois
    df_resultado = pd.concat([df_ano1, df_ano2], ignore_index=True).drop_duplicates()

    return valores_comuns, df_resultado

# Agrupa os resultados da função anterior em um didiocnario
def agrupar_estados_por_valor(df):
    """
    Recebe um DataFrame com colunas ['Estado', 'Valor', 'Ano']
    e retorna um dicionário {Valor: [lista de estados]}
    agrupando os estados pelo valor.
    """
    dicionario_valores = (
        df.groupby('Valor')['Estado']
        .apply(lambda x: sorted(x.unique()))
        .to_dict()
    )
    return dicionario_valores

# Função Completa que compara as colunas e identifica os valores que são iguais e armazena em um dicionario
def comparar_varios_trilemas_com_detalhes(df, colunas_trilema, casas=4):
    df_local = df.copy()

    # Truncar todas as colunas especificadas
    for col in colunas_trilema:
        df_local[col] = truncar(df_local[col], casas)

    # Estrutura para armazenar os resultados
    dicionario_total = defaultdict(lambda: {'estados': set(), 'comparacoes': set()})

    # Comparar todos os pares únicos de colunas
    for i in range(len(colunas_trilema)):
        for j in range(i + 1, len(colunas_trilema)):
            col1 = colunas_trilema[i]
            col2 = colunas_trilema[j]

            for idx, linha in df_local.iterrows():
                v1 = linha[col1]
                v2 = linha[col2]

                if v1 == v2:
                    estado = linha['Estado']
                    dicionario_total[v1]['estados'].add(estado)
                    dicionario_total[v1]['comparacoes'].add((col1, col2))

            # Também comparar valores comuns entre colunas (mesmo que em estados diferentes)
            set1 = set(df_local[col1].unique())
            set2 = set(df_local[col2].unique())
            valores_comuns = set1 & set2

            for valor in valores_comuns:
                estados1 = df_local[df_local[col1] == valor]['Estado'].unique()
                estados2 = df_local[df_local[col2] == valor]['Estado'].unique()

                dicionario_total[valor]['estados'].update(estados1)
                dicionario_total[valor]['estados'].update(estados2)
                dicionario_total[valor]['comparacoes'].add((col1, col2))

    # Converter sets em listas ordenadas
    return {
        valor: {
            'estados': sorted(info['estados']),
            'comparacoes': sorted(info['comparacoes'])
        }
        for valor, info in dicionario_total.items()
    }


def carregar_resultado_valores_comuns():
    caminho = os.path.join(os.path.dirname(__file__), 'resultado.json')
    with open(caminho, 'r', encoding='utf-8') as f:
        resultado = json.load(f)
    return {float(k): v for k, v in resultado.items()}
