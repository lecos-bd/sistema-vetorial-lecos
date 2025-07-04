import pandas as pd
import numpy as np

# Ler o arquivo Excel
df = pd.read_excel('Planilha Geral - Índice Trilema Brasil.xlsx', sheet_name='Trilema energético')


# Derreter os dados filtrados para Equidade, Segurança e Ambiental
def tratamento_equidade():
    df_equidade = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Equidade 2018', 'Equidade 2019', 'Equidade 2020', 'Equidade 2021', 'Equidade 2022'],
        var_name='Dimensão',
        value_name='Escala'
    )
    df_equidade['Ano'] = df_equidade['Dimensão'].str.slice(-4)
    return df_equidade

def tratamento_seguranca():
    df_seguranca = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Segurança 2018', 'Segurança 2019', 'Segurança 2020', 'Segurança 2021', 'Segurança 2022'],
        var_name='Dimensão',
        value_name='Escala'
    )
    df_seguranca['Ano'] = df_seguranca['Dimensão'].str.slice(-4)

    return df_seguranca

def tratamento_ambiental():
    df_ambiental = pd.melt(
        df,
        id_vars=['Região', 'Estado'],
        value_vars=['Ambiental 2018', 'Ambiental 2019', 'Ambiental 2020', 'Ambiental 2021', 'Ambiental 2022'],
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
