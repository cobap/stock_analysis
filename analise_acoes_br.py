import fundamentos as ftos
import pandas as pd
import requests
import numpy as np

# Bastante diferença entre os dados

def get_tickers():

    url = 'http://fundamentus.com.br/detalhes.php'
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.get(url, headers=header)

    tickets = pd.read_html(r.text)[0]
    return tickets

def calcula_cagr(series, anos):

    # Caso anos seja maior que len(series), isso dará problema
    series = series.fillna(0)
    res = (series[-1] / series[-anos])**(1/anos) - 1
    if res == np.nan:
        res = 0
    return round(res, 2)

dados = []
tickers = get_tickers()['Papel']

i = 0
for ticker in tickers:
    if i > 100:
        break
    i += 1
    try:
        temp = ftos.get_fundamentos(ticker)
        dados.append(temp)
    except:
        pass

resultados = pd.DataFrame()
menos_5_anos = []
for empresa in dados:

    ticker = empresa.columns.names[1]
    if len(empresa.index) < 5:
        menos_5_anos.append(ticker)
        continue

    print('Processando...', ticker)
    caixa = empresa['Caixa']['Dinheiro em Caixa']
    caixa_cagr_3anos = calcula_cagr(caixa, 3)
    caixa_cagr_5anos = calcula_cagr(caixa, 5)

    fcf = empresa['Fluxo de Caixa']['FCF']
    fcf_cagr_3anos = calcula_cagr(fcf, 3)
    fcf_cagr_5anos = calcula_cagr(fcf, 5)

    fco = empresa['Fluxo de Caixa']['FCO']
    fco_cagr_3anos = calcula_cagr(fco, 3)
    fco_cagr_5anos = calcula_cagr(fco, 5)

    ll = empresa['Resultados']['Lucro Líquido']
    ll_cagr_3anos = calcula_cagr(ll, 3)
    ll_cagr_5anos = calcula_cagr(ll, 5)

    rl = empresa['Resultados']['Receita Líquida']
    rl_cagr_3anos = calcula_cagr(rl, 3)
    rl_cagr_5anos = calcula_cagr(rl, 5)

    try:
        margem = empresa['Resultados']['Margem EBITDA']
        margem_cagr_3anos = calcula_cagr(margem, 3)
        margem_cagr_5anos = calcula_cagr(margem, 5)
    except:
        try:
            margem = empresa['Resultados']['Margem EBIT']
            margem_cagr_3anos = calcula_cagr(margem, 3)
            margem_cagr_5anos = calcula_cagr(margem, 5)
        except:
            margem_cagr_3anos = np.nan
            margem_cagr_5anos = np.nan

    try:
        dl_ebitda = empresa['Dívida']['DL/EBITDA']
        dl_ebitda_cagr_3anos = calcula_cagr(dl_ebitda, 3)
        dl_ebitda_cagr_5anos = calcula_cagr(dl_ebitda, 5)
    except:
        dl_ebitda_cagr_3anos = np.nan
        dl_ebitda_cagr_5anos = np.nan

    dl = empresa['Dívida']['Dívida Líquida']
    dl_cagr_3anos = calcula_cagr(dl, 3)
    dl_cagr_5anos = calcula_cagr(dl, 5)

    resultados = resultados.append({'ticker':ticker, 'caixa_cagr_3anos': caixa_cagr_3anos, 'caixa_cagr_5anos': caixa_cagr_5anos, 'fcf_cagr_3anos': fcf_cagr_3anos, 'fcf_cagr_5anos': fcf_cagr_5anos, 'fco_cagr_3anos': fco_cagr_3anos, 'fco_cagr_5anos': fco_cagr_5anos, 'll_cagr_3anos': ll_cagr_3anos, 'll_cagr_5anos': ll_cagr_5anos, 'rl_cagr_3anos': rl_cagr_3anos, 'rl_cagr_5anos': rl_cagr_5anos, 'margem_cagr_3anos': margem_cagr_3anos, 'margem_cagr_5anos': margem_cagr_5anos, 'dl_ebitda_cagr_3anos': dl_ebitda_cagr_3anos, 'dl_ebitda_cagr_5anos': dl_ebitda_cagr_5anos, 'dl_cagr_3anos': dl_cagr_3anos, 'dl_cagr_5anos': dl_cagr_5anos
    }, ignore_index=True)

"""
Analisando Empresas com LucroLiquido CAGR 5 e CAGR 3 positivo
"""

# Toodas tem mais de 5 anos de bolsa

# Tem que filtrar empresas que tem PREJUIZO

# Todas tem lucro liquido de 5 anos e 3 anos crescente
boas_empresas = resultados[(resultados.ll_cagr_3anos > 0) & (resultados.ll_cagr_5anos > 0)].copy()

# Todas tem que ter receita subindo
boas_empresas = boas_empresas[(boas_empresas.rl_cagr_3anos > 0) & (boas_empresas.rl_cagr_5anos > 0)].copy()

boas_empresas
