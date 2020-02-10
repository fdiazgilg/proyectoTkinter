import configparser
import sys
import json
import requests
from tkinter import messagebox
from requests.exceptions import HTTPError

#Lectura del fichero de configuración config.py
config = configparser.ConfigParser()
config.read('config.ini')

#Variables clave
APIKEY = config.get('PRODUCTION', 'SECRET_KEY')
URL_API_LOAD = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={}&symbol=BTC,ETH,XRP,LTC,BCH,BNB,USDT,EOS,BSV,XLM,ADA,TRX'
URL_API_CONV = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'

#Función que obtiene las criptomonedas de la API
def getCrypto():
    resp = requests.get(URL_API_LOAD.format(APIKEY))
    try:
        resp.raise_for_status()
        js = resp.text
        response = json.loads(js)
        values = response.get('data')
        return values

    except requests.exceptions.RequestException as e:
        messagebox.showerror(message="Error: {}".format(e), title="API Error")
        sys.exit()


#Invocamos al API para realizar la conversión indicando los valores necesarios
def priceConv(valueQ, cryptoFR, cryptoTO):
    resp = requests.get(URL_API_CONV.format(valueQ, cryptoFR, cryptoTO, APIKEY))
    try:
        js = resp.text
        response = json.loads(js)
        resp.raise_for_status()
        values = response.get('data')
        quote = values['quote']
        conver = quote[cryptoTO]
        rate = conver['price']
        return rate

    except requests.exceptions.HTTPError as e:
        js = resp.text
        response = json.loads(js)
        error = resp.status_code
        state = response['status']
        code = state['error_code']
        message = state['error_message']
        messagebox.showerror(message="Price Conversion HTTP Error: {}".format(e), title="API Error")
        #messagebox.showerror(message="Price Conversion HTTP Error {}: Code <{}> {}".format(error, code, message), title="API Error")
        return False