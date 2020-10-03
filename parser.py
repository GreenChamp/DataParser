import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


def labelStrip(x):
    x = x[:x.find('(')]
    return x


def percentStrip(x):
    x = float(x[:-1]) * 0.01
    return x


driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.investing.com/indices/rts-cash-settled-futures-technical')
time.sleep(10)
# popup = driver.find_element_by_xpath('/html/body/div[7]/div[1]/span/i')
# popup.click()
time_button = driver.find_element_by_xpath('//*[@id="timePeriodsWidget"]/li[2]/a')

# Oil
url_oil = 'https://www.investing.com/commodities/brent-oil'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
response_oil = requests.get(url_oil, headers=headers)
tree_oil = bs(response_oil.content, 'html.parser')
quotes_oil = tree_oil.find('div', {'class': 'top bold inlineblock'})
items_oil = quotes_oil.find_all('span')
cur_oil = float(items_oil[0].text.replace(',', ''))

# USD
url_usd = 'https://www.investing.com/currencies/usd-rub'
response_usd = requests.get(url_usd, headers=headers)
tree_usd = bs(response_usd.content, 'html.parser')
quotes_usd = tree_usd.find('div', {'class': 'top bold inlineblock'})
items_usd = quotes_usd.find_all('span')
cur_usd = float(items_usd[0].text.replace(',', ''))

# S&P500
url_spx = 'https://www.investing.com/indices/us-spx-500-futures'
response_spx = requests.get(url_spx, headers=headers)
tree_spx = bs(response_spx.content, 'html.parser')
quotes_spx = tree_spx.find('div', {'class': 'top bold inlineblock'})
items_spx = quotes_spx.find_all('span')
cur_spx = float(items_spx[0].text.replace(',', ''))

page_source = driver.page_source
tree = bs(page_source, 'html.parser')
quotes = tree.find('div', {'class': 'top bold inlineblock'})
items = quotes.find_all('span')
cur_price = float(items[0].text.replace(',', ''))

time.sleep(300)

res = []
for i in range(100):
    time_button.click()
    page_source = driver.page_source
    tree = bs(page_source, 'html.parser')

    quotes = tree.find('div', {'class': 'top bold inlineblock'})
    items = quotes.find_all('span')
    res.append({'Price': items[0].text.replace(',', '')})
    res.append({'Daily Change': items[1].text})
    res.append({'Daily % Change': percentStrip(items[-1].text)})
    res.append({'Current Change': float(items[0].text.replace(',', '')) - cur_price})
    cur_price = float(items[0].text.replace(',', ''))

    ind = tree.find('table', {'class': 'genTbl closedTbl technicalIndicatorsTbl smallTbl float_lang_base_1'})
    table = ind.find('tbody')
    rows = table.find_all('tr')[:-1]
    for row in rows:
        res.append(
            {labelStrip(row.find('td', {'class': 'first left symbol'}).text): row.find('td', {'class': 'right'}).text})

    response_oil = requests.get(url_oil, headers=headers)
    tree_oil = bs(response_oil.content, 'html.parser')
    quotes_oil = tree_oil.find('div', {'class': 'top bold inlineblock'})
    items_oil = quotes_oil.find_all('span')
    res.append({'Oil Current Change': float(items_oil[0].text.replace(',', '')) - cur_oil})
    res.append({'Oil Price': float(items_oil[0].text.replace(',', ''))})
    res.append({'Daily Oil Change': items_oil[1].text})
    res.append({'Daily Oil % Change': percentStrip(items_oil[-1].text)})
    cur_oil = float(items_oil[0].text.replace(',', ''))

    response_usd = requests.get(url_usd, headers=headers)
    tree_usd = bs(response_usd.content, 'html.parser')
    quotes_usd = tree_usd.find('div', {'class': 'top bold inlineblock'})
    items_usd = quotes_usd.find_all('span')
    res.append({'USD Current Change': float(items_usd[0].text.replace(',', '')) - cur_usd})
    res.append({'USD Price': float(items_usd[0].text.replace(',', ''))})
    res.append({'Daily USD Change': items_usd[1].text})
    res.append({'Daily USD % Change': percentStrip(items_usd[-1].text)})
    cur_usd = float(items_usd[0].text.replace(',', ''))

    response_spx = requests.get(url_spx, headers=headers)
    tree_spx = bs(response_spx.content, 'html.parser')
    quotes_spx = tree_spx.find('div', {'class': 'top bold inlineblock'})
    items_spx = quotes_spx.find_all('span')
    res.append({'SPX Current Change': float(items_spx[0].text.replace(',', '')) - cur_spx})
    res.append({'SPX Price': float(items_spx[0].text.replace(',', ''))})
    res.append({'Daily SPX Change': items_spx[1].text})
    res.append({'Daily SPX % Change': percentStrip(items_spx[-1].text)})
    cur_spx = float(items_spx[0].text.replace(',', ''))

    time.sleep(300)

    page_source = driver.page_source
    tree = bs(page_source, 'html.parser')

    quotes = tree.find('div', {'class': 'top bold inlineblock'})
    items = quotes.find_all('span')
    res.append({'Result': float(items[0].text.replace(',', '')) - cur_price})

    fin = {}
    for d in res:
        fin.update(d)
    df = pd.DataFrame(fin, index=[i])
    if i == 0:
        df_fin = df
    else:
        df_fin = pd.concat([df_fin, df])

df_fin.to_csv('RTS.csv')
