"""
Análise dos fundamentos das empresas dos EUA
"""

import requests

"""
Informações básicas como setor, CEO, etc
"""
def get_company_details(ticker='AAPL'):
    url = 'https://financialmodelingprep.com/api/v3/company/profile/{0}'.format(ticker)
    return requests.get(url).json()


"""
Retorna E.V por quarter ou anual
"""
def get_enterprise_value(ticker, quarter=False):

    url = None
    if quarter:
        url = 'https://financialmodelingprep.com/api/v3/enterprise-value/{0}?period=quarter'.format(ticker)
    else:
        url = 'https://financialmodelingprep.com/api/v3/enterprise-value/{0}'.format(ticker)

    return requests.get(url).json()['enterpriseValues']


"""
Recupera KPIs principais das empresas
"""
def get_company_key_metrics(ticker, quarter=False):

    url = None
    if quarter:
        url = 'https://financialmodelingprep.com/api/v3/company-key-metrics/{0}?period=quarter'.format(ticker)
    else:
        url = 'https://financialmodelingprep.com/api/v3/company-key-metrics/{0}'.format(ticker)

    return requests.get(url).json()['metrics']


"""
Recupera informações de crescimento da empresa ano após ano
"""
def get_company_growth_results(ticker, quarter=False):

    url = None
    if quarter:
        url = 'https://financialmodelingprep.com/api/v3/financial-statement-growth/{0}?period=quarter'.format(ticker)
    else:
        url = 'https://financialmodelingprep.com/api/v3/financial-statement-growth/{0}'.format(ticker)

    return requests.get(url).json()['growth']


"""
Avaliação da empresa de acordo com vários aspectos
"""
def get_company_rating(ticker):

    url = 'https://financialmodelingprep.com/api/v3/company/rating/{0}'.format(ticker)
    return requests.get(url).json()


"""
Retornar DCF da companhia, histórico ou não, ou quarter ou não
"""
def get_company_dcf(ticker, quarter=False, historical=False):

    url = None
    if historical:
        url = 'https://financialmodelingprep.com/api/v3/company/historical-discounted-cash-flow/{0}'.format(ticker)
    else:
        url = 'https://financialmodelingprep.com/api/v3/company/discounted-cash-flow/{0}'.format(ticker)

    if historical and quarter:
        url = url + '?period=quarter'

    requests.get(url).json()







for _result in get_enterprise_value('AAPL')['enterpriseValues']:
    print(_result['date'])

get_company_growth_results('AAPL')
