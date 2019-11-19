import pandas as pd
import os, requests, re, time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# ML Libraries
from sklearn.cluster import KMeans

os.chdir('C:\\Users\\antonio.coelho\\codigos\\stock_analysis')

def stock_details(stock):

    detalhes = dict()
    # stock = 'KROT3'

    res = requests.get('https://www.fundamentus.com.br/detalhes.php?papel={0}'.format(stock))
    soup = BeautifulSoup(res.text, 'html.parser')
    table_rows = soup.findAll('tr')

    # Verificamos se retornou alguma coisa, caso não, é um empty dataframe
    if len(table_rows) <= 2:
        return detalhes

    # Dados Gerais
    detalhes['cotacao_dia'] = table_rows[0].findAll('td')[3].span.text
    detalhes['ultimo_pregao'] = table_rows[1].findAll('td')[3].span.text
    detalhes['menor_cotacao_12_meses'] = table_rows[2].findAll('td')[3].span.text
    detalhes['maior_cotacao_12_meses'] = table_rows[3].findAll('td')[3].span.text
    detalhes['volume_medio_2_meses'] = table_rows[4].findAll('td')[3].span.text
    detalhes['valor_mercado'] = table_rows[5].findAll('td')[1].span.text
    detalhes['ultimo_balanco'] = table_rows[5].findAll('td')[3].span.text
    detalhes['enterprise_value'] = table_rows[6].findAll('td')[1].span.text
    detalhes['soma_total_acoes'] = table_rows[6].findAll('td')[3].span.text

    # Oscilações
    detalhes['variacao_dia'] = table_rows[8].findAll('td')[1].span.text
    detalhes['variacao_mes'] = table_rows[9].findAll('td')[1].span.text
    detalhes['variacao_30_dias'] = table_rows[10].findAll('td')[1].span.text
    detalhes['variacao_12_meses'] = table_rows[11].findAll('td')[1].span.text
    detalhes['variacao_2019'] = table_rows[12].findAll('td')[1].span.text
    detalhes['variacao_2018'] = table_rows[13].findAll('td')[1].span.text
    detalhes['variacao_2017'] = table_rows[14].findAll('td')[1].span.text
    detalhes['variacao_2016'] = table_rows[15].findAll('td')[1].span.text
    detalhes['variacao_2015'] = table_rows[16].findAll('td')[1].span.text
    detalhes['variacao_2014'] = table_rows[17].findAll('td')[1].span.text

    # Fundamentalista
    detalhes['preco_lucro'] = table_rows[8].findAll('td')[3].span.text
    detalhes['lucro_por_acao'] = table_rows[8].findAll('td')[5].span.text

    detalhes['preco_valorpatrimonial'] = table_rows[9].findAll('td')[3].span.text
    detalhes['vpa'] = table_rows[9].findAll('td')[5].span.text

    detalhes['p_ebit'] = table_rows[10].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['margem_bruta'] = table_rows[10].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['psr'] = table_rows[11].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['margem_ebit'] = table_rows[11].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['p_ativos'] = table_rows[12].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['margem_liquida'] = table_rows[12].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['p_capital_giro'] = table_rows[13].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['ebit_ativo'] = table_rows[13].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['p_ativo_circ_liq'] = table_rows[14].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['roic'] = table_rows[14].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['dividend_yeild'] = table_rows[15].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['roe'] = table_rows[15].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['ev_ebit'] = table_rows[16].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['liquidez_corr'] = table_rows[16].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['giro_ativos'] = table_rows[17].findAll('td')[3].span.text.replace('\n', '').strip()
    detalhes['dividabruta_patrimonio'] = table_rows[17].findAll('td')[5].span.text.replace('\n', '').strip()

    detalhes['crescimento_receita'] = table_rows[18].findAll('td')[3].span.text.replace('\n', '').strip()

    return detalhes

def limpa_dataframe():

    stock_list = pd.read_excel('b3_stock_list.xlsx')
    stock_list.columns = ['SETOR', 'SUBSETOR', 'SEGMENTO', 'CODIGO', 'TIPO_ACAO']

    stock_list = stock_list.iloc[1:, :]

    stock_list['SETOR'] = stock_list.SETOR.ffill()
    stock_list['SUBSETOR'] = stock_list.SUBSETOR.ffill()

    stock_list = stock_list[~stock_list['CODIGO'].isna()]
    stock_list = stock_list[stock_list['CODIGO'] != 'LISTAGEM']
    stock_list = stock_list[~stock_list['SEGMENTO'].isna()]

    return stock_list

def _filtra_stocks(stock_list):

    """
    Return [0] - All except BDR
    """

    stocks_drn = stock_list[stock_list['TIPO_ACAO'] == 'DRN']
    stocks_dr3 = stock_list[stock_list['TIPO_ACAO'] == 'DR3']
    stocks_nm = stock_list[stock_list['TIPO_ACAO'] == 'NM             ']
    stocks_m2 = stock_list[stock_list['TIPO_ACAO'] == 'M2']
    stocks_mb = stock_list[stock_list['TIPO_ACAO'] == 'MB             ']

    stocks_n2 = stock_list[stock_list['TIPO_ACAO'] == 'N2']
    stocks_n2 = stocks_n2.append(stock_list[stock_list['TIPO_ACAO'] == 'N2             '])
    stocks_n2['TIPO_ACAO'] = 'N2'

    stocks_n1 = stock_list[stock_list['TIPO_ACAO'] == 'N1']
    stocks_n1 = stocks_n1.append(stock_list[stock_list['TIPO_ACAO'] == 'N1             '])
    stocks_n1['TIPO_ACAO'] = 'N1'

    stocks_ma = stock_list[stock_list['TIPO_ACAO'] == 'MA']
    stocks_ma = stocks_ma.append(stock_list[stock_list['TIPO_ACAO'] == 'MA             '])
    stocks_ma['TIPO_ACAO'] = 'MA'

    all_except_bdr = stocks_nm.append(stocks_m2).append(stocks_mb).append(stocks_n2).append(stocks_n1).append(stocks_ma)

    return all_except_bdr

def recupera_stock_perdidos(nome_stocks_processados):

    # nome_stocks_processados = 'detalhes_stock_20191111.xlsx'
    stocks_processados = pd.read_excel(nome_stocks_processados)
    stocks_processados['CODIGO']

    stock_list = limpa_dataframe()
    stock_list = stock_list[~stock_list['TIPO_ACAO'].isna()]
    stock_list = _filtra_stocks(stock_list)

    lista_processados = stocks_processados.apply(lambda row: row['CODIGO'][:-1:], axis=1)

    nao_processados = stock_list[~stock_list['CODIGO'].isin(lista_processados)]
    return nao_processados['CODIGO']

def roda_pendencias(lista_nao_processados):

    stocks_detailed = pd.DataFrame()

    # Pegamos os detalhes para todos os códigos da B3
    for _ticker in lista_nao_processados:

        # Como não sabemos se é 3 ou 4, tentamos os 2 para todas as ações
        _ticket_to_test = _ticker + '3'
        _details = stock_details(_ticket_to_test)
        _details['CODIGO'] = _ticket_to_test
        stocks_detailed = stocks_detailed.append(_details, ignore_index=True)
        time.sleep(3)

        _ticket_to_test = _ticker + '4'
        _details = stock_details(_ticket_to_test)
        _details['CODIGO'] = _ticket_to_test
        stocks_detailed = stocks_detailed.append(_details, ignore_index=True)
        time.sleep(3)

        print('-- Finalizado processamento para {0} --'.format(_ticker))

    print('Finalizado processamento total')
    return stocks_detailed

def recupera_dados_stock(nome_arquivo):

    stock_list = limpa_dataframe()

    # Verificar quais são as classificadas como NA
    stock_list = stock_list[~stock_list['TIPO_ACAO'].isna()]

    # Tiramos BDR
    stock_list = _filtra_stocks(stock_list)

    # DataFrame de controle
    stocks_detailed = pd.DataFrame()

    # Pegamos os detalhes para todos os códigos da B3
    for _ticker in stock_list['CODIGO']:

        # Como não sabemos se é 3 ou 4, tentamos os 2 para todas as ações
        _ticket_to_test = _ticker + '3'
        _details = stock_details(_ticket_to_test)
        _details['CODIGO'] = _ticket_to_test
        stocks_detailed = stocks_detailed.append(_details, ignore_index=True)
        time.sleep(3)

        _ticket_to_test = _ticker + '4'
        _details = stock_details(_ticket_to_test)
        _details['CODIGO'] = _ticket_to_test
        stocks_detailed = stocks_detailed.append(_details, ignore_index=True)
        time.sleep(3)

        print('-- Finalizado processamento para {0} --'.format(_ticker))

    print('Finalizado processamento total')

    stocks_detailed = stocks_detailed[~stocks_detailed['cotacao_dia'].isna()]

    stocks_detailed.to_excel(nome_arquivo)

    return stocks_detailed

def _transform_stringcolumn_tonumber(nome_coluna):

    nome_coluna = nome_coluna.str.replace('%', '')
    nome_coluna = nome_coluna.str.replace('.', '@')
    nome_coluna = nome_coluna.str.replace(',', '.')
    nome_coluna = nome_coluna.str.replace('@', '')
    nome_coluna = nome_coluna.apply(lambda row: 0 if len(row) == 1 else row)
    nome_coluna = nome_coluna.astype(float)
    return nome_coluna

def _transform_comma_topoint(nome_coluna):

    nome_coluna = nome_coluna.apply(lambda row: 0 if len(row) == 1 else row)
    nome_coluna = nome_coluna.str.replace('.', '@')
    nome_coluna = nome_coluna.str.replace(',', '.')
    nome_coluna = nome_coluna.str.replace('@', '').astype(float)

    return nome_coluna

if __name__ == '__main__':

    columns_name = [
        'Index', 'CODIGO', 'cotacao_dia', 'crescimento_receita (%)', 'dividabruta_patrimonio', 'dividend_yeild (%)', 'ebit_ativo (%)', 'enterprise_value',
        'ev_ebit', 'giro_ativos', 'liquidez_corr', 'lucro_por_acao', 'maior_cotacao_12_meses', 'margem_bruta', 'margem_ebit',
        'margem_liquida', 'menor_cotacao_12_meses', 'p_ativo_circ_liq', 'p_ativos', 'p_capital_giro', 'p_ebit', 'preco_lucro',
        'preco_valorpatrimonial', 'psr', 'roe', 'roic', 'soma_total_acoes', 'ultimo_balanco', 'ultimo_pregao', 'valor_mercado',
        'variacao_12_meses', 'variacao_2014 (%)', 'variacao_2015 (%)', 'variacao_2016 (%)', 'variacao_2017 (%)', 'variacao_2018 (%)', 'variacao_2019 (%)',
        'variacao_30_dias (%)', 'variacao_dia (%)', 'variacao_mes (%)', 'volume_medio_2_meses', 'vpa'
    ]
    dados_novembro = pd.read_excel('detalhes_stock_20191111.xlsx', names=columns_name)
    dados_novembro = dados_novembro.iloc[:, 1:]

    # Tranforma alguma colunas % em float
    colunas_remover_porcentagem = ['crescimento_receita (%)', 'dividend_yeild (%)', 'ebit_ativo (%)', 'variacao_2014 (%)', 'variacao_2015 (%)', 'variacao_2016 (%)', 'variacao_2017 (%)', 'variacao_2018 (%)', 'variacao_2019 (%)', 'variacao_30_dias (%)', 'variacao_dia (%)', 'variacao_mes (%)', 'margem_bruta', 'margem_ebit', 'margem_liquida', 'roe', 'roic', 'variacao_12_meses']
    for coluna in colunas_remover_porcentagem:
        dados_novembro[coluna] = _transform_stringcolumn_tonumber(dados_novembro[coluna])

    colunas_mudar_virgula_ponto = ['cotacao_dia', 'dividabruta_patrimonio', 'enterprise_value', 'ev_ebit', 'giro_ativos', 'liquidez_corr', 'lucro_por_acao', 'maior_cotacao_12_meses', 'menor_cotacao_12_meses', 'p_ativo_circ_liq', 'p_ativos', 'p_capital_giro', 'p_ebit', 'preco_lucro', 'preco_valorpatrimonial', 'psr', 'soma_total_acoes', 'valor_mercado', 'volume_medio_2_meses', 'vpa']
    for coluna in colunas_mudar_virgula_ponto:
        dados_novembro[coluna] = _transform_comma_topoint(dados_novembro[coluna])



    """
    EDA - Tratamento de dados
    """
    corr = dados_novembro.corr()
    corr.style.background_gradient(cmap='coolwarm')
    metricas_basicas = dados_novembro[['vpa', 'roic', 'roe', 'margem_ebit', 'lucro_por_acao', 'CODIGO']]

    plt.scatter(metricas_basicas.iloc[:,0], metricas_basicas.iloc[:,1])
    metricas_basicas[metricas_basicas.iloc[:,0] > 20000]



    """
    Tentando um ML básico para clusterização sem préprocessamento
    """
    knn_basico = dados_novembro[['vpa', 'roic', 'roe', 'margem_ebit', 'lucro_por_acao']]
    kmeans = KMeans(n_clusters=4, random_state=0).fit(knn_basico)
    kmeans.cluster_centers_
    labels = kmeans.predict(knn_basico)









# https://queroficarrico.com/blog/ferramentas-gratuitas-para-analise-fundamentalista/
# https://www.fundamentus.com.br/detalhes.php?papel=PETR3
