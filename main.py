# Ler depois
# https://www.learndatasci.com/tutorials/python-finance-part-3-moving-average-trading-strategy/
# Esse bem importante, explicando como calcular
# https://towardsdatascience.com/trading-toolbox-02-wma-ema-62c22205e2a9
# https://github.com/areed1192/sigma_coding_youtube/blob/master/python/python-data-science/machine-learning/random-forest/random_forest_price_prediction.ipynb
import os, requests, math
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import plot_roc_curve
from sklearn.metrics import accuracy_score, classification_report
os.chdir('C:\\Users\\Antonio Coelho\\Codigos\\stock_analysis')

# TODO: 1º Coletar os dados das ações
# TODO: 2º Transformação dos dados
# TODO: 3º Tornar um problema de regressão em classificação
# TODO: 4º Criação da R.F p/ predição como classificação
# TODO: 5º Trabalhar com algoritmos genéticos p/ criação da população de R.F

token = 'apikey=d297cd796ed9bda6081954060cb42e92'

def detalhes_companhia(ticker='AAPL'):
    url = 'https://financialmodelingprep.com/api/v3/company/profile/{0}?{1}'.format(ticker, token)
    return requests.get(url).json()

def metricas_principais_companhia(ticker, quarter=False):

    url = None
    if quarter:
        url = 'https://financialmodelingprep.com/api/v3/company-key-metrics/{0}?period=quarter&{1}'.format(ticker, token)
    else:
        url = 'https://financialmodelingprep.com/api/v3/company-key-metrics/{0}?{1}'.format(ticker, token)

    return requests.get(url).json()['metrics']


# Escolhemos as empresas que vamos pegar os dados e baixamos os dados do periodo selecionado
empresas = ['AAPL', 'MSFT', 'AMZN']
dados_original = yf.download(empresas,'2010-01-04','2014-12-10')

# Agora pegamos somente dados de fechamento
dados = dados_original['Adj Close']
dados_full = dados_original[['Adj Close', 'Volume', 'High', 'Low']].stack().reset_index()
"""
##############################
ANÁLISE EXPLORATÓRIA DOS DADOS
##############################
"""

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

"""
#######################
TRANSFORMAÇÃO DOS DADOS
#######################
"""

# Filtramos pelas ações da AAPL
dados_aapl = dados_full[dados_full['level_1'] == 'AAPL']
dados_aapl.drop(['level_1'], axis=1, inplace=True)

# Para calcular médias móveis
dados_medias_moveis_20 = dados_aapl['Adj Close'].rolling(window=20).mean()
dados_medias_moveis_100 = dados_aapl['Adj Close'].rolling(window=300).mean()

# Para calcular médias móveis exponenciais
dados_ema_20 = dados_aapl['Adj Close'].ewm(span=20, adjust=False).mean()
dados_ema_50 = dados_aapl['Adj Close'].ewm(span=150, adjust=False).mean()

# Juntamos todos os dados em uma df só
dados_medias_moveis = pd.concat([dados_ema_20, dados_ema_50, dados_medias_moveis_20, dados_medias_moveis_100], axis=1)
dados_medias_moveis.columns = ['EMA_20', 'EMA_50', 'MA_20', 'MA_100']

dados_aapl = pd.concat([dados_aapl, dados_medias_moveis], axis=1)

# Vamos usar um signal flag para identificar onde a média movel exponencial trouxe um valor distinto do resultado da ação nos últimos X dias
dados_aapl['Flag_EMA_20'] = np.sign(dados_aapl['EMA_20'].diff(20))
dados_aapl['Flag_EMA_50'] = np.sign(dados_aapl['EMA_50'].diff(50))

# Por ultimo calculamos a diferença de fechamento do mercado p/ cada dia
dados_aapl['Mudança Preço'] = dados_aapl['Adj Close'].diff()

"""
##############################
CALCULANDO MÉTRICAS DO MERCADO
##############################
"""

################
# Calculo do RSI
################

df_alta, df_baixa = dados_aapl[['Mudança Preço']].copy(), dados_aapl[['Mudança Preço']].copy()
df_alta.loc[df_alta['Mudança Preço'] < 0, 'Mudança Preço'] = 0
df_baixa.loc[df_baixa['Mudança Preço'] > 0, 'Mudança Preço'] = 0

# Tornamos os valores negativos absolutos antes de continuar o cálculo
df_baixa['Mudança Preço'] = df_baixa['Mudança Preço'].abs()

df_alta_ewm = df_alta.ewm(span=14, adjust=False).mean()
df_baixa_ewm = df_baixa.ewm(span=14, adjust=False).mean()

rs = df_alta_ewm / df_baixa_ewm
rsi = 100.0 - (100.0 / (1.0 + rs))

dados_aapl['Dias Baixa'] = df_baixa['Mudança Preço']
dados_aapl['Dias Alta'] = df_alta['Mudança Preço']
dados_aapl['RSI'] = rsi


##################################
# Calculo do oscilador estocástico
##################################

df_alta, df_baixa = dados_aapl[['High']].copy(), dados_aapl[['Low']].copy()

# Aplicamos a média movel e pegamos a mínima e a máxima
df_baixa = df_baixa.rolling(window=14).min()
df_alta = df_alta.rolling(window=14).max()

dados_aapl['baixa_14'] = df_baixa
dados_aapl['alta_14'] = df_alta

# Calculamos o oscilador estocástico
k_percent = 100 * ((dados_aapl['Adj Close'] - dados_aapl['baixa_14']) / (dados_aapl['alta_14'] - dados_aapl['baixa_14']))

# Add the info to the data frame.
dados_aapl['K%'] = k_percent


########################
# Calculo do Williams %R
########################

# Calculate William %R indicator.
r_percent = ((dados_aapl['alta_14'] - dados_aapl['Adj Close']) / (dados_aapl['alta_14'] - dados_aapl['baixa_14'])) * - 100

# Add the info to the data frame.
dados_aapl['Williams %R'] = r_percent



#################
# Calculo do MACD
#################

# Calculamos o MACD genérico
macd = dados_aapl['Adj Close'].ewm(span=12, adjust=False).mean() - dados_aapl['Adj Close'].ewm(span=26, adjust=False).mean()

# Pegamos agora a média exponencial de 9 periodos do MACD
macd_9_ewm = macd.ewm(span=9).mean()

dados_aapl['MACD'] = macd
dados_aapl['MACD_EMA_9'] = macd_9_ewm


#################################
# Calculando Price Rate Of Change
#################################

dados_aapl['PROC'] = dados_aapl['Adj Close'].pct_change(periods=9)


##############################
# Calculando On Balance Volume
##############################


volume = dados_aapl['Volume']
mudanca = dados_aapl['Adj Close'].diff()

# Inicializamos o OBV p/ o cálculo
prev_obv = 0
obv_values = []

# Para cada conjunto voluma e mudança no preço
for i, j in zip(mudanca, volume):

    if i > 0:
        current_obv = prev_obv + j
    elif i < 0:
        current_obv = prev_obv - j
    else:
        current_obv = prev_obv

    # OBV.append(current_OBV)
    prev_obv = current_obv
    obv_values.append(current_obv)

# Criamos agora a Series usando o index inicial dos dados aapl
obv_values = pd.Series(obv_values, index=dados_aapl.index)
obv_values.name = 'OBV'
dados_aapl = pd.concat([dados_aapl, obv_values], axis=1)



"""
#########################
RECUPERA DADOS DO MERCADO
#########################
"""

# Puxamos todas as métricas históricas da empresa
metricas_aapl = metricas_principais_companhia('AAPL', quarter=True)

# Definimos quais vão ser as novas colunas e adicionamos no dataset
novas_colunas = list(metricas_aapl[0].keys())
dados_aapl = pd.concat([dados_aapl, pd.DataFrame(columns=novas_colunas)])

# Identificamos o ano e o quarter
quarter = (dados_aapl['Date'].dt.month - 1)//3
anos = dados_aapl['Date'].dt.year
dados_aapl['Quarter'] = quarter
dados_aapl['Anos'] = anos.astype('str')

# Para cada métrica respectiva aquele ano e quarter, adicionamos na respectiva linha
for metrica in metricas_aapl:
    quarter = (int(metrica['date'][5:7]) - 1)//3
    ano = metrica['date'][:4]
    dados_aapl.loc[(dados_aapl['Anos'] == ano) & (dados_aapl['Quarter'] == quarter), novas_colunas] = list(metrica.values())

dados_aapl.to_excel('dataframe_aapl.xlsx')



"""
#################
CRIAÇÃO DO MODELO
#################
"""

novas_colunas = ['date', 'Revenue per Share', 'Net Income per Share', 'Operating Cash Flow per Share', 'Free Cash Flow per Share', 'Cash per Share', 'Book Value per Share', 'Tangible Book Value per Share', 'Shareholders Equity per Share', 'Interest Debt per Share', 'Market Cap', 'Enterprise Value', 'PE ratio', 'Price to Sales Ratio', 'POCF ratio', 'PFCF ratio', 'PB ratio', 'PTB ratio', 'EV to Sales', 'Enterprise Value over EBITDA', 'EV to Operating cash flow', 'EV to Free cash flow',
 'Earnings Yield', 'Free Cash Flow Yield', 'Debt to Equity', 'Debt to Assets', 'Net Debt to EBITDA', 'Current ratio', 'Interest Coverage', 'Income Quality', 'Dividend Yield', 'Payout Ratio', 'SG&A to Revenue', 'R&D to Revenue', 'Intangibles to Total Assets', 'Capex to Operating Cash Flow', 'Capex to Revenue', 'Capex to Depreciation', 'Stock-based compensation to Revenue', 'Graham Number', 'Graham Net-Net', 'Working Capital', 'Tangible Asset Value', 'Net Current Asset Value',
 'Invested Capital', 'Average Receivables', 'Average Payables', 'Average Inventory', 'Capex per Share'
]


dados_aapl = pd.read_excel('./dataframe_aapl.xlsx')
dados_aapl.drop(['Unnamed: 0'], axis=1, inplace=True)

# Nosso modelo quer prever se o proximo dia é um dia de alta ou de baixa, para saber se deve comprar ou vender ações
dados_aapl['Label'] = np.sign(dados_aapl['Adj Close'].diff())
# Aqui podemos definir dias que não teve variação, como dias de compra
dados_aapl.loc[dados_aapl['Label'] == 0.0] = 1.0

# Perdemos cerca de 25% dos dados, mas ficamos sem nenhum NA no Dataset
len(dados_aapl)
len(dados_aapl.dropna())

dados_aapl = dados_aapl.dropna()



# Separação das colunas de predição (label) e das colunas de fato
colunas_x = ['RSI','K%','Williams %R','PROC','MACD','MACD_EMA_9', 'OBV'] + novas_colunas
colunas_x.remove('date')
X = dados_aapl.loc[:, colunas_x]

y = dados_aapl['Label']

# Temos 55 colunas p/ trabalhar
len(X.columns)



# Vamos separar os dados X e Y em 30% 70%
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)


# Criamos a RandomForest
rf_model = RandomForestClassifier(n_estimators=100, oob_score=True, criterion="gini", random_state=42)

# Damos Fit nos dados
rf_model.fit(X_train, y_train)

# Fazemos as predições
y_pred = rf_model.predict(X_test)


# Vamos medir acurácia do modelo
print('Correct Prediction (%): ', accuracy_score(y_test, rf_model.predict(X_test), normalize=True) * 100.0)

# Montamos o report da classificação
report = classification_report(y_true = y_test, y_pred = y_pred, target_names=['Dia Baixa', 'Dia Alta'], output_dict = True)
pd.DataFrame(report).transpose()


"""
###################
MELHORANDO O MODELO
###################
"""

importancia_features = pd.Series(rf_model.feature_importances_, index=X.columns).sort_values(ascending=False)
importancia_features

plt.plot(importancia_features)

###################
# Randomized Search
###################

n_estimators = list(range(200, 2000, 200))
max_features = ['auto', 'sqrt', None, 'log2']
max_depth = list(range(10, 110, 10))
max_depth.append(None)
min_samples_split = [2, 5, 10, 20, 30, 40]
min_samples_leaf = [1, 2, 7, 12, 14, 16 ,20]
bootstrap = [True, False]

# Montamos o grid de busca agora:
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

rf_random_search = RandomForestClassifier()
rf_random = RandomizedSearchCV(estimator=rf_random_search, param_distributions=random_grid, n_iter=100, cv=3, verbose=2, random_state=42, n_jobs=-1)
rf_random.fit(X_train, y_train)

# Fazemos as predições
y_pred = rf_random.predict(X_test)

# Vamos medir acurácia do modelo
print('Correct Prediction (%): ', accuracy_score(y_test, rf_random.predict(X_test), normalize=True) * 100.0)

# Montamos o report da classificação
report = classification_report(y_true = y_test, y_pred = y_pred, target_names=['Dia Baixa', 'Dia Alta'], output_dict = True)
pd.DataFrame(report).transpose()


# Para implementar corretamenta algoritmos genéticos precisamos definir algumas coisas

"""
TAMANHO POPULAÇÃO: 100 RF ao mesmo tempo
OPERADORES GENÉTICOS:
    - Vamos usar crossover de N pontos
    - Vamos usar mutação
    -
FUNÇÃO FITNESS: Nesse caso, a melhor função fitness é aquela que gera maior acurácia para nosso modelo. E o lado bom de usar RF - não precisamos nos preocupar com overfitting
"""


"""
# Variáveis possiveis no RF
    n_estimators: int
    criterion: binary (ou gini ou entropy)
    max_depth: int (0~inf)
    min_samples_split: int maior que 2
    min_samples_leaf: int maior que 1
    max_features: int
    {
        sqrt(n_features)
        log2(n_features)
    }
"""

# Vamos precisar de um cromosso que consiga contar tudo isso sem gerar casos inválidos
# Nesse caso nosso cromossomo será composto por números binários

def _cria_cromossomo():

    # Template do cromossomo
    # AAAAAAAA-B-CCCCCCC-DDDDDDD-EEEEEEE-F


    n_estimadores = random.randint(0, 255)
    criterio = random.randint(0, 1)
    profundidade_maxima = random.randint(0, 127)
    minimo_splits = random.randint(0, 127)
    minimo_folhas = random.randint(0, 127)
    maximo_features = random.randint(0, 1)

    mapping_criterio = {0: 'gini', 1: 'entropy'}
    mapping_features = {0: 'sqrt', 1: 'log2'}

    cromossomo = n_estimadores, mapping_criterio[criterio], profundidade_maxima, minimo_splits, minimo_folhas, mapping_features[maximo_features]
    return cromossomo


def cria_inviduo_aleatorio():

    cromossomo = _cria_cromossomo()
    rf = RandomForestClassifier(n_estimators=cromossomo[0] + 1, criterion=cromossomo[1], max_depth=cromossomo[2] + 1, min_samples_split=cromossomo[3] + 2, min_samples_leaf=cromossomo[4] + 1, max_features=cromossomo[5])
    return rf


def get_cromossomo_individuo(rf):

    mapping_criterio = {'gini': '1', 'entropy': '0'}
    mapping_features = {'sqrt': '1', 'log2': '0'}

    n_estimadores = '{0:08b}'.format(rf.n_estimators)
    criterio = mapping_criterio[rf.criterion]
    profundidade_maxima = '{0:07b}'.format(rf.max_depth)
    minimo_splits = '{0:07b}'.format(rf.min_samples_split)
    minimo_folhas = '{0:07b}'.format(rf.min_samples_leaf)
    maximo_features = mapping_features[rf.max_features]

    return n_estimadores + criterio + profundidade_maxima + minimo_splits + minimo_folhas + maximo_features


def set_cromossomo_individuo(cromossomo):

    # Modelo AAAAAAAA-B-CCCCCCC-DDDDDDD-EEEEEEE-F

    mapping_criterio = {'0': 'gini', '1': 'entropy'}
    mapping_features = {'0': 'sqrt', '1': 'log2'}

    return RandomForestClassifier(n_estimators=int(cromossomo[:8], 2) + 1, criterion=mapping_criterio[cromossomo[8:9]], max_depth=int(cromossomo[9:16], 2) + 1, min_samples_split=int(cromossomo[16:23], 2) + 2, min_samples_leaf=int(cromossomo[23:30], 2) + 1, max_features=mapping_features[cromossomo[30:31]])


def crossover(gene1, gene2, tipo='dois_pontos'):

    # gene1 = get_cromossomo_individuo(populacao[0])
    # gene2 = get_cromossomo_individuo(populacao[1])

    if tipo == 'um_ponto':
        ponto_separacao = random.randint(1, 30)
        filho1 = gene1[:ponto_separacao] + gene2[ponto_separacao:]
        filho2 = gene2[:ponto_separacao] + gene1[ponto_separacao:]

    if tipo == 'dois_pontos':
        ponto_separacao_1, ponto_separacao_2 = 1, 1
        while(ponto_separacao_1 >= ponto_separacao_2):
            ponto_separacao_1 = random.randint(1, 30)
            ponto_separacao_2 = random.randint(1, 30)

        filho1 = gene2[:ponto_separacao_1] + gene1[ponto_separacao_1:ponto_separacao_2] + gene2[ponto_separacao_2:]
        filho2 = gene1[:ponto_separacao_1] + gene2[ponto_separacao_1:ponto_separacao_2] + gene1[ponto_separacao_2:]

    if tipo == 'uniforme':

        # REVIEW implementação crossover uniforme
        # Geramos quais serão os pontos de crossover
        # template = list(np.random.randint(2, size=31))
        filho1 = ['1' if (x=='1' and y=='1') else '0' for x, y in zip(gene1, gene2)]
        filho2 = ['0' if (x=='0' and y=='0') else '1' for x, y in zip(gene1, gene2)]

    return filho1, filho2


def funcao_fitness(rf, X, y):
    rf.fit(X, y)
    return accuracy_score(y, rf.predict(X), normalize=True) * 100.0


def selecao_natural(populacao, fitness_populacao, numero_filhos, taxa_mutacao, tipo='roleta_viciada', tipo_crossover='dois_pontos'):

    filhos = []

    if tipo == 'roleta_viciada':

        fitness_total = np.sum(fitness_populacao)
        roleta_invividuos = fitness_populacao / fitness_total

        for novo_filho in range(0, numero_filhos):

            chance_mutacao = random.random()

            # Definimos quem são os pais
            sorteio = random.random()
            pai1 = np.argmax((sorteio - roleta_invividuos.cumsum()) < 0)
            sorteio = random.random()
            pai2 = np.argmax((sorteio - roleta_invividuos.cumsum()) < 0)

            # Aplicamos crossover
            cromossomo_pai_1 = get_cromossomo_individuo(populacao[pai1])
            cromossomo_pai_2 = get_cromossomo_individuo(populacao[pai2])

            # Vamos adicionar só o primeiro filho aqui na lista
            filho = crossover(cromossomo_pai_1, cromossomo_pai_2, tipo=tipo_crossover)[random.randint(0, 1)]

            # Rodamos a mutação
            if (chance_mutacao < taxa_mutacao):
                gene_mutante = random.randint(0,30)
                fenotipo_mutante = '0' if filho[gene_mutante] == '1' else '1'
                filho = filho[:gene_mutante] + fenotipo_mutante + filho[gene_mutante+1:]

            filhos.append(filho)

    return filhos


def cria_populacao(tamanho_populacao):

    populacao = []
    for rf in list(range(0, tamanho_populacao)):
        populacao.append(cria_inviduo_aleatorio())

    return populacao



# TODO: Calcular convergencia genética
# TODO: Implementar eletismo
# TODO: Implementar forma de manter individuos com maior diversidade genética

# Variáveis p/ rodar simulação
iteracao = 0
limite_iteracoes = 1000
tamanho_populacao = 50
taxa_mutacao = 0.05
X = X_train
y = y_train

populacao = cria_populacao(tamanho_populacao)
rating_populacao = []

while(True):

    # Calculamos o fitness da populacao total
    fitness_populacao = [funcao_fitness(rf, X, y) for rf in populacao]
    rating_populacao.append(np.sum(fitness_populacao))

    # Geramos a nova populacao
    qtd_novos_filhos = round(tamanho_populacao * 0.7)
    novos_filhos = selecao_natural(populacao, fitness_populacao, qtd_novos_filhos, 0.005)


    # Aplicação elitismo
    melhores_arvores = fitness_populacao > np.quantile(fitness_populacao, 0.7)
    populacao = [arvore for arvore, fitness in zip(populacao, melhores_arvores) if fitness == True]

    # Tornamos a lista totalmente aleatória, e vamos remover alguns pais p/ entrada dos filhos
    # random.shuffle(populacao)
    # for individuo_morto in range(0, qtd_novos_filhos):
    #     populacao.pop()


    # Agora adicionamos todos os filhos
    rf_filhos = [set_cromossomo_individuo(_cromo) for _cromo in novos_filhos]
    populacao.extend(rf_filhos)
    random.shuffle(populacao)

    # TODO: Aqui devemos calcular a convergencia genetica
    # TODO: Calcular de tivemos um ranting de fitness da populacao melhor que na rodada anterior

    # Calculamos mais um na iteracao, e vemos se já passamos do threshold
    iteracao += 1
    if (iteracao > limite_iteracoes):
        break
    elif (iteracao % 10 == 0):
        taxa_mutacao = math.cos(iteracao + 3.1415) + 1
        print('RODADA {0}'.format(iteracao))


x = list(range(1, len(rating_populacao) +1))
plt.plot(x, rating_populacao)
