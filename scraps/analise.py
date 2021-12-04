import os
import pandas as pd
import numpy as np
os.chdir('C:\\Users\\Antonio Coelho\\Codigos\\stock_analysis')

def ajusta_dataset(dataframe):

    tem_divida = False
    tem_roic = False
    # Transformamos valores numericos em float
    if 'EV/EBIT' in dataframe.index:
        dataframe.loc['EV/EBIT'] = dataframe.loc['EV/EBIT'].str.replace('.', '')
        dataframe.loc['EV/EBIT'] = dataframe.loc['EV/EBIT'].str.replace(',', '.').astype('float64')

    if 'ROIC' in dataframe.index:
        dataframe.loc['ROIC'] = dataframe.loc['ROIC'].str.replace(',', '.').str.strip('%').astype('float64') / 100
        tem_roic = True

    if 'DB/PL' in dataframe.index:
        dataframe.loc['DB/PL'] = dataframe.loc['DB/PL'].str.replace(',', '.').astype('float64')
        tem_divida = True

    if 'PSR' in dataframe.index:
        dataframe.loc['PSR'] = dataframe.loc['PSR'].str.replace(',', '.').astype('float64')

    dataframe.loc['P/L'] = dataframe.loc['P/L'].str.replace('.', '')
    dataframe.loc['P/L'] = dataframe.loc['P/L'].str.replace(',', '.').astype('float64')

    dataframe.loc['P/VPA'] = dataframe.loc['P/VPA'].str.replace('.', '')
    dataframe.loc['P/VPA'] = dataframe.loc['P/VPA'].str.replace(',', '.').astype('float64')

    dataframe.loc['P/FCO'] = dataframe.loc['P/FCO'].str.replace('.', '')
    dataframe.loc['P/FCO'] = dataframe.loc['P/FCO'].str.replace(',', '.').astype('float64')

    dataframe.loc['LC'] = dataframe.loc['LC'].str.replace('.', '')
    dataframe.loc['LC'] = dataframe.loc['LC'].str.replace(',', '.').astype('float64')

    dataframe.loc['LPA'] = dataframe.loc['LPA'].str.replace('.', '')
    dataframe.loc['LPA'] = dataframe.loc['LPA'].str.replace(',', '.').astype('float64')

    dataframe.loc['VPA'] = dataframe.loc['VPA'].str.replace('.', '')
    dataframe.loc['VPA'] = dataframe.loc['VPA'].str.replace(',', '.').astype('float64')

    dataframe.loc['DPA'] = dataframe.loc['DPA'].str.replace('.', '')
    dataframe.loc['DPA'] = dataframe.loc['DPA'].str.replace(',', '.').astype('float64')

    # E depois porcentagens em números relativos
    dataframe.loc['DY'] = dataframe.loc['DY'].str.replace(',', '.').str.replace('%', '').astype('float64') / 100
    dataframe.loc['ROE'] = dataframe.loc['ROE'].str.replace(',', '.').str.strip('%').astype('float64') / 100

    return tem_divida, tem_roic

ihqs = pd.DataFrame()
empresas = []

# Calculamos a metrica de IHQs para cada empresa
for empresa in os.listdir('historico_empresas/'):
    historico = pd.read_excel('historico_empresas/' + empresa, index_col=0)

    empresas.append(empresa.split('_')[1])

    # Arrumamos as linhas e colunas do dataset p/ poder trabalhar com os dados
    tem_divida, tem_roic = ajusta_dataset(historico)

    ihq1 = (historico.loc['LC'] / 1.5)
    roic = historico.loc['ROIC'] if tem_roic else 1
    ihq2 = (historico.loc['P/L'] * roic)
    ihq3 = historico.loc['DB/PL'] if tem_divida else 0.0001
    ihq4 = (historico.loc['P/VPA'] / 1.5)
    IHQ = (ihq1 * ihq2) / ((ihq3 * ihq4) + 0.001)
    ihqs = ihqs.append(IHQ, ignore_index=True)

ihqs.index = empresas

# Removemos os outliers, depois vamos entender o que aconteceu
ihqs = ihqs.drop(['BBAS3', 'BBDC3', 'SMLS3'], axis=0)

# Versão original dos IHQs
ihqs.to_excel('ihqs_historico.xlsx')

# Versão original dos IHQs
ihqs['Ticker'] = ihqs.index
ihqs_melted = ihqs.melt(id_vars=['Ticker'], var_name='Ano', value_name='IHQ')
ihqs_melted.to_excel('ihqs_historico_melted.xlsx')
