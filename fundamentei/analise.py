#%%

import pandas as pd

#%%

# Tickers que tinhamos que ter os dados
tickers = pd.read_csv('tickers.txt', header=None, names=['ticker'])

# Lemos o arquivo de resultados
empresas = pd.read_csv('resultados.csv', sep='|', index_col=0)

empresas = pd.merge(tickers, empresas, on='ticker', how='left')

#%%

# Arrumamos o rating para inteiro
empresas.rating = pd.to_numeric(
    empresas.rating.str.split('/').str[0].fillna('-1'))

# Arrumamos quantidade de ratings
empresas.qtd_rating = pd.to_numeric(
    empresas.qtd_rating.fillna('-1'))

#%%

# Limpamos os valores nulos
empresas.df_dict = empresas.df_dict.fillna('{}')

# Avaliamos os dicionários e transformamos tudo em dataframes
empresas['dataframe'] = empresas.df_dict.apply(eval).apply(pd.DataFrame)

#%%

# Formula para CARG (Compound Annual Growth Rate) = (UltimoValor / PrimeiroValor) ^ (1/Anos) - 1

# Criamos uma lambda para calcular CARG
carg = lambda ultimo, primeiro, anos: (ultimo / primeiro) ** (1/anos) - 1

# Função que valida se o dataframe é valido e retorna o resultado
def calcula_carg(dataframe: pd.DataFrame, categoria: str):
    
    # Vemos se tem chave de receita
    if categoria not in dataframe.columns:
        return -1
    
    # Pegamos quantidade de anos
    anos = len(dataframe)

    # Pegamos os valores
    primeiro = dataframe[categoria][0]
    ultimo = dataframe[categoria][anos-1]

    return f'{carg(ultimo, primeiro, anos):.2f}'


# Função que calcula a média das margens do dataframe
def calcula_media_margem(dataframe: pd.DataFrame):

    if 'Net Mar.' not in dataframe.columns:
        return ''
    
    margens = pd.to_numeric(dataframe['Net Mar.'].str.replace('%', '').str.replace(',', '.').str.replace('L', '-1'))

    return f'{margens.mean():.0f}'
    

#%%

empresas['cagr_receita'] = empresas.dataframe.apply(
    lambda x: calcula_carg(x, categoria='Revenue'))

empresas['cagr_lucro'] = empresas.dataframe.apply(
    lambda x: calcula_carg(x, categoria='Net Inc.'))

empresas['media_margem'] = empresas.dataframe.apply(
    lambda x: calcula_media_margem(x))

#%%

empresas.drop(['df_dict', 'dataframe'], axis=1).to_excel('resultados_consolidados.xlsx', index=False)

