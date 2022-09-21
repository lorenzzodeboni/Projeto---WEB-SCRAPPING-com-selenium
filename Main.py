#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)


# In[2]:


df = pd.read_excel('buscas.xlsx')
df


# Definindo a função para busca no google shopping

# In[3]:


def busca_google_shopping(navegador, produto, termos_banidos, preco_min, preco_max):
    # tratando os temos da tabela
    preco_min = float(preco_min)
    preco_max = float(preco_max)
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_banidos = termos_banidos.split()
    lista_termos_produtos = produto.split()
    
    # entrando no google 
    navegador.get('https://www.google.com.br/')
      
    # pesquisando o produto no google
    navegador.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(produto)
    navegador.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(Keys.ENTER)
    
    # clicando na aba shopping
    elementos = navegador.find_elements(By.CLASS_NAME, 'hdtb-mitem')
    for item in elementos:
        if 'Shopping' in item.text:
            item.click()
            break
    
    # pegando a lista de resultados no google shopping
    lista_resultados = navegador.find_elements(By.CLASS_NAME, 'i0X6df')
    
    # pegando informações da lista
    lista_ofertas = []
    for produto in lista_resultados:
        nome = produto.find_element(By.CLASS_NAME, 'Xjkr3b').text
        preco = produto.find_element(By.CLASS_NAME, 'a8Pemb').text
        elemento_link = produto.find_element(By.CLASS_NAME, 'aULzUe')
        elemento_pai = elemento_link.find_element(By.XPATH, '..')
        link = elemento_pai.get_attribute('href')
        nome = nome.lower() 

        # verificacao do nome
        tem_termos_banidos = False
        for palavra in lista_termos_banidos:
            if palavra in nome:
                tem_termos_banidos = True

        tem_todos_termos_produto = True
        for palavra in lista_termos_produtos:
            if palavra not in nome:
                tem_todos_termos_produto = False

    # se tem termos banidos = false e tem todos os temos do produto = true     
    # tratando a formatacao do preco
        if tem_termos_banidos == False and tem_todos_termos_produto == True:
            try:
                preco = preco.replace("R$", "").replace(" ", "").replace('.','').replace(",", ".")
                preco = float(preco)
                
            except:
                continue

    # verificando se o preco está dentro do minimo e do maximo e atualiza a lista de ofertas
            if preco >= preco_min and preco <= preco_max:
                lista_ofertas.append((nome, preco, link))
                
    return lista_ofertas


# In[4]:


def busca_buscape(navegador, produto, termos_banidos, preco_min, preco_max):
    # tratando os temos da tabela
    preco_min = float(preco_min)
    preco_max = float(preco_max)
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_banidos = termos_banidos.split()
    lista_termos_produtos = produto.split()
    
    # entrando no buscape 
    navegador.get('https://www.buscape.com.br/')
    

    # pesquisar o produto no buscape
    navegador.find_element(By.XPATH, '//*[@id="new-header"]/div[1]/div/div/div[3]/div/div/div[2]/div/div[1]/input').send_keys(produto, Keys.ENTER)   
   
    # pegando a lista de resultados no buscape
    time.sleep(3)
    lista_resultados = navegador.find_elements(By.CLASS_NAME, 'SearchCard_ProductCard_Inner__7JhKb')
    
    # separando os resultados
    lista_ofertas = []
    for produto in lista_resultados:
        nome = produto.find_element(By.CLASS_NAME, 'Text_Text__bOTfK ').text
        preco = produto.find_element(By.CLASS_NAME, 'Text_MobileHeadingSAtLarge__dJqgU').text
        link = produto.get_attribute('href')
        nome = nome.lower() 


        # verificacao do nome
        tem_termos_banidos = False
        for palavra in lista_termos_banidos:
            if palavra in nome:
                tem_termos_banidos = True

        tem_todos_termos_produto = True
        for palavra in lista_termos_produtos:
            if palavra not in nome:
                tem_todos_termos_produto = False

        # se tem termos banidos = false e tem todos os temos do produto = true     
        # tratando a formatacao do preco
        if tem_termos_banidos == False and tem_todos_termos_produto == True:
            preco = preco.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            preco = float(preco)

            # verificando se o preco está dentro do minimo e do maximo e atualiza a lista de ofertas
            if preco >= preco_min and preco <= preco_max:
                lista_ofertas.append((nome, preco, link))
                
    return lista_ofertas


# In[5]:


tabela_ofertas = pd.DataFrame()

for linha in df.index:
    produto = df.loc[linha, 'Nome']
    termos_banidos = df.loc[linha, 'Termos banidos']
    preco_min = df.loc[linha, 'Preço mínimo']
    preco_max = df.loc[linha, 'Preço máximo']
    lista_ofertas_google = busca_google_shopping(navegador,produto,termos_banidos, preco_min, preco_max)
    if lista_ofertas_google:
        tabela_google = pd.DataFrame(lista_ofertas_google, columns = ['produto', 'preco', 'link'])
        tabela_ofertas = tabela_ofertas.append(tabela_google)
    else:
        tabela_google = None

    lista_ofertas_buscape = busca_buscape(navegador,produto,termos_banidos, preco_min, preco_max)
    if lista_ofertas_buscape:
        tabela_buscape = pd.DataFrame(lista_ofertas_buscape, columns = ['produto', 'preco', 'link'])
        tabela_ofertas = tabela_ofertas.append(tabela_buscape)
    else:
        tabela_buscape = None

display(tabela_ofertas)


# In[6]:


tabela_ofertas = tabela_ofertas.reset_index(drop=True)
tabela_ofertas.to_excel('Gabarito ofertas.xlsx', index = False)

navegador.quit()
