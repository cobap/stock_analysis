import pandas as pd
import os, requests, re
from bs4 import BeautifulSoup

os.chdir('C:\\Users\\212587697\\Box Sync\\Personal\\Finance Analysis')

def stock_details(stock):

    detalhes = dict()

    res = requests.get('https://www.fundamentus.com.br/detalhes.php?papel={0}'.format(stock))
    soup = BeautifulSoup(res.text, 'html.parser')
    table_rows = soup.findAll('tr')

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

def _filtra_stocks(stocks):

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

if __name__ == '__main__':

    stock_list = limpa_dataframe()

    # Verificar quais são as classificadas como NA
    stock_list[stock_list['TIPO_ACAO'].isna()]

    stock_list = _filtra_stocks()
    stocks_detailed = pd.DataFrame()

    stock_list[stock_list['CODIGO'] == 'PETR']

    _details = stock_details('PETR4')
    _details['CODIGO'] = 'PETR'

    stocks_detailed.append(_details, ignore_index=True)

    # https://queroficarrico.com/blog/ferramentas-gratuitas-para-analise-fundamentalista/
    # https://www.fundamentus.com.br/detalhes.php?papel=PETR3
