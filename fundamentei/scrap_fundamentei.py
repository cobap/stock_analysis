#%%

import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#%%

# Métodos interação com fundamentei
def aguarda(xpath_elemento_espera, tempo_espera=3):

    try:

        wait = WebDriverWait(driver, tempo_espera)

        elemento = EC.visibility_of_element_located(
            (By.XPATH, xpath_elemento_espera))

        elemento = wait.until(elemento)

        if elemento:
            return True

    except:
        return False


def login():

    email = '/html/body/div/div/div/div/div[2]/div[2]/form/input[1]'
    senha = '/html/body/div/div/div/div/div[2]/div[2]/form/input[2]'

    email = driver.find_element_by_xpath(email)
    email.send_keys('baptistaacbc@gmail.com')

    senha = driver.find_element_by_xpath(senha)
    senha.send_keys('a1b2c3d4')

    driver.find_element_by_xpath(
        '/html/body/div/div/div/div/div[2]/div[2]/form/button').click()

    # Esperarmos login acontecer
    return aguarda('/html/body/div/div[1]/div/div/div/nav/div[2]/ul/li[1]/a')


def get_acao_us(ticker):

    driver.get(f'https://fundamentei.com/us/{ticker}')

    # Precisamos esperar a página carregar 100%
    status = aguarda('/html/body/div/div[2]/div[3]/div/div/div/div/div[1]/div[1]/h3')

    if not status:
        return False

    # Componentes que interessam
    rating = driver.find_element_by_class_name('css-h1iaj5')
    qtd_ratings = driver.find_element_by_class_name('css-ydmqo4')

    # Convertemos em valores
    rating = rating.text

    qtd_ratings = qtd_ratings.find_element_by_tag_name('strong').text

    # Tabela de resultados
    tabela = driver.find_element_by_tag_name('table')

    tabela = pd.read_html('<table>' + tabela.get_attribute('innerHTML') + '</table>')
    tabela = tabela[0]

    print(f'-- Finalizando {ticker} --')

    return rating, qtd_ratings, tabela.to_dict()


#%%

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://fundamentei.com/login")


status = login()

tickers = pd.read_csv('tickers.txt', header=None, names=['tickers'])

resultados = []

if status:

    for ticker in tickers.tickers.values:
        if resultado := get_acao_us(ticker):
            resultado = list(resultado)
            resultado.append(ticker)
            resultados.append(resultado)
            time.sleep(10)
        else:
            logging.info(f'-- Ticker {ticker} com problema --')

driver.quit()

dados = pd.DataFrame(resultados, columns=['rating', 'qtd_rating', 'df_dict', 'ticker'])
dados.to_csv('resultados.csv', sep='|')

#%%
