import os, time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests_random_user_agent

os.chdir('C:\\Users\\Antonio Coelho\\Codigos\\stock_analysis')
driver = webdriver.PhantomJS()

def recupera_lista_acoes_ocean():

    url_base = 'https://www.oceans14.com.br/acoes/'
    driver.get(url_base)
    driver.save_screenshot("screenshot.png")

    tabela_de_acoes = driver.find_element_by_id(id_='t1')
    linhas_tabela_de_acoes = tabela_de_acoes.find_elements(By.TAG_NAME, "tr")

    empresas, links, nomes_empresa, segmentos = [], [], [], []

    for index in range(1, len(linhas_tabela_de_acoes) - 1):
        empresas.append(driver.find_element_by_xpath('//*[@id="t1"]/tbody/tr[{}]/td[1]'.format(index)).text)
        links.append(driver.find_element_by_xpath('//*[@id="t1"]/tbody/tr[{}]/td[1]/a'.format(index)).get_attribute("href"))
        nomes_empresa.append(driver.find_element_by_xpath('//*[@id="t1"]/tbody/tr[{}]/td[2]'.format(index)).text)
        segmentos.append(driver.find_element_by_xpath('//*[@id="t1"]/tbody/tr[{}]/td[4]'.format(index)).get_attribute('textContent'))

    dados_ocean = pd.DataFrame({'empresas': empresas,'links': links,'nome_empresa': nomes_empresa,'segmento': segmentos})
    dados_ocean.to_excel('dados_ocean.xlsx')


# Vemos cada empresa da lista da Ocean
dados_ocean = pd.read_excel('dados_ocean.xlsx', index=None)


# Vamos tentar fazer um teste com o VALE
link_historico = dados_ocean.iloc[0, :]['links']
# Entramos no site e pegamos detalhes do histórico da vale
driver.get(link_historico)
driver.save_screenshot("screenshot.png")








empresas_index_ibovespa = [
    'BBSE3','VRML3','BBDC4','BBDC3','BRAP4','BBAS3','BRKM5','BRFS3','CCRO3','CMIG4','CIEL3','CSAN3','CVCB3','CYRE3','ECOR3','ELET3','ELET6','EMBR3','ENBR3','ENGIE3','EQTL3','YDUQ3','FLRY3','GGBR4','GOAU4','GOLL4','HYPE3','IGTA3','IRBR3','ITSA4','ITUB4','JBSS3','KLBN11','KROT3','RENT3','LAME4','LREN3','MGLU3','MRFG3','MRVE3','MULT3','NATU3','PCAR4','PETR4','PETR3','BRDT3','QUAL3','RADL3','RAIL3','SBSP3','SANB11','CSNA3','SMLS3','SUZB5','TAEE11','VIVT4','TIMP3','UGPA3','USIM5','VALE3','VVAR3','WEGE3'
]

acoes_que_nao_deram_certo = ['VRML3','BRAP4','BRKM5','CMIG4','ELET6','ENGIE3','GGBR4','ITSA4','ITUB4','KLBN11','KROT3','NATU3','PETR4','SANB11','VIVT4','USIM5']


def get_dados_historico_qual(ticker):

    url_base = 'https://vicenteguimaraes.penserico.com/dashboard/cp.pr?e={}'.format(ticker)
    driver.get(url_base)

    tabela_historico = None
    # Agora vamos pra tabela com o histórico de indicativos
    try:
        tabela_historico = driver.find_element_by_id(id_='tabqualitativos')
    except:
        print('ERRO AO BUSCAR HISTÓRICO DA AÇÃO... {}'.format(ticker))
        return False

    # Vemos de quando é o histórico da empresa
    header_tabela = tabela_historico.find_elements(By.TAG_NAME, "thead")[0].find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "th")[1]
    ano_inicial = int(header_tabela.get_attribute('innerHTML'))

    # Encontramos a tabela dentro dos dados qualitativos
    linhas_tabela_historico = tabela_historico.find_elements(By.TAG_NAME, "tbody")[0]

    # detalhes_tabela_historico = linhas_tabela_historico.find_elements(By.TAG_NAME, "td")
    # Agora buscamos por linha nossos dados
    detalhes_tabela_historico = linhas_tabela_historico.find_elements(By.TAG_NAME, "tr")

    _linha, _coluna = [], []
    linhas = []

    for linha in detalhes_tabela_historico:

        # Para cada linha, pegamos os dados de toda a colunas
        colunas_tabela_historico = linha.find_elements(By.TAG_NAME, "td")

        linhas.append(linha.find_elements(By.TAG_NAME, "th")[0].find_elements(By.TAG_NAME, "span")[0].get_attribute('innerHTML'))

        for coluna in colunas_tabela_historico:
            res = coluna.find_elements(By.TAG_NAME, 'span')[1].get_attribute('innerHTML').replace('\n', '')
            _linha.append(res)
        _coluna.append(_linha)
        _linha = []

    # Para o número de colunas, definimos o header
    dados = pd.DataFrame(_coluna, index=linhas)
    dados = dados.iloc[:, :-1]
    dados.columns = ['{}'.format(ano_inicial-x) for x in range(0, len(dados.columns))]

    dados.to_excel('historico_{0}_quali.xlsx'.format(ticker))

print('Terminou geral')


for empresa in empresas_index_ibovespa:
    get_dados_historico_qual(empresa)
    print('Finalizando {}'.format(empresa))
    time.sleep(5)
