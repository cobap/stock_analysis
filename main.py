# Ler depois
# https://www.learndatasci.com/tutorials/python-finance-part-3-moving-average-trading-strategy/
# Esse bem importante, explicando como calcular
# https://towardsdatascience.com/trading-toolbox-02-wma-ema-62c22205e2a9

import os
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


# Escolhemos as empresas que vamos pegar os dados e baixamos os dados do periodo selecionado
empresas = ['AAPL', 'MSFT', 'AMZN']
dados_original = yf.download(empresas,'2010-01-04','2014-12-10')

# Agora pegamos somente dados de fechamento
dados = dados_original['Adj Close']


dados['AAPL'].plot()

dados_stacked = dados.stack().reset_index()
dados_stacked.columns = ['Data','Ticker','Preço']
sns.lineplot(x='Data', y='Preço', hue='Ticker',data=dados_stacked)


# Para calcular médias móveis
dados_medias_moveis_20 = dados.rolling(window=20).mean()
dados_medias_moveis_100 = dados.rolling(window=300).mean()

# Para calcular médias móveis exponenciais
dados_ema_20 = dados.ewm(span=20, adjust=False).mean()
dados_ema_50 = dados.ewm(span=150, adjust=False).mean()


dados_apple = pd.concat([dados['AAPL'], dados_medias_moveis_20['AAPL'], dados_medias_moveis_100['AAPL']], axis=1)
dados_apple.columns = ['APPL', 'APPL_MM20', 'APPL_MM100']
dados_apple = dados_apple.stack().reset_index()
dados_apple.columns = ['Data','Ticker','Preço']
sns.lineplot(x='Data', y='Preço', hue='Ticker',data=dados_apple)


dados_apple = pd.concat([dados['AAPL'], dados_medias_moveis_20['AAPL'], dados_medias_moveis_100['AAPL'], dados_ema_20['AAPL'], dados_ema_50['AAPL']], axis=1)
dados_apple.columns = ['AAPL', 'AAPL_MM20', 'AAPL_MM100', 'AAPL_EMA20', 'AAPL_EMA50']
dados_apple = dados_apple.stack().reset_index()
dados_apple.columns = ['Data','Ticker','Preço']
sns.lineplot(x='Data', y='Preço', hue='Ticker',data=dados_apple)
