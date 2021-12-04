#%%

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#%%

# Métodos interação com fundamentei

def login():

    email = '/html/body/div/div/div/div/div[2]/div[2]/form/input[1]'
    senha = '/html/body/div/div/div/div/div[2]/div[2]/form/input[2]'

    email = driver.find_element_by_xpath(email)
    email.send_keys('baptistaacbc@gmail.com')

    senha = driver.find_element_by_xpath(senha)
    senha.send_keys('a1b2c3d4')

    driver.find_element_by_xpath(
        '/html/body/div/div/div/div/div[2]/div[2]/form/button').click()

    try:
        
        wait = WebDriverWait(driver, 10)

        elemento_login = EC.visibility_of_element_located(
            (By.XPATH, '/html/body/div/div[1]/div/div/div/nav/div[2]/ul/li[1]/a'))

        elemento_login = wait.until(elemento_login)
        
        if elemento_login:
            return True
    
    except:
        return False


def get_acao_us(ticker):

    driver.get(f'https://fundamentei.com/us/{ticker}')

    # Componentes que interessam
    rating = '/html/body/div/div[2]/div[4]/div/div/div/div/div[1]/div[1]/h3'
    qtd_ratings = '/html/body/div/div[2]/div[4]/div/div/div/div/div[1]/div[3]/p/strong'

    


#%%

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://fundamentei.com/login")

status = login()

if status:

    get_acao_us('aapl')

#%%
