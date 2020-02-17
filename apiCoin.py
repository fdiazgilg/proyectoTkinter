import configparser
import sys
import json
import requests
import utilities
from tkinter import messagebox
from requests.exceptions import HTTPError


#Lectura del fichero de configuración config.py
config = configparser.ConfigParser()
config.read('config.ini')

#Variables clave
APIKEY = config.get('PRODUCTION', 'SECRET_KEY')
URL_API_LOAD = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={}&symbol=BTC,ETH,XRP,LTC,BCH,BNB,USDT,EOS,BSV,XLM,ADA,TRX'
URL_API_CONV = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount=1&symbol={}&convert={}&CMC_PRO_API_KEY={}'


#Función que obtiene las criptomonedas de la API
def getCrypto():
    resp = requests.get(URL_API_LOAD.format(APIKEY))
    js = resp.text
    response = json.loads(js)
    try:
        resp.raise_for_status()
        js = resp.text
        response = json.loads(js)
        values = response.get('data')
        return values

    except:
        errorCode = resp.status_code
        errorMessage = utilities.apiErrors(errorCode, response)
        messagebox.showerror(message="{}".format(errorMessage), title="API Error")
        sys.exit()


#Invocamos al API para realizar la conversión indicando los valores necesarios
def priceConv(cryptoFR, cryptoTO):
    resp = requests.get(URL_API_CONV.format(cryptoFR, cryptoTO, APIKEY))
    js = resp.text
    response = json.loads(js)
    try:
        resp.raise_for_status()
        values = response.get('data')
        quote = values['quote'][cryptoTO]['price']

        return quote

    except:
        errorCode = resp.status_code
        errorMessage = utilities.apiErrors(errorCode, response)
        messagebox.showerror(message="{}".format(errorMessage), title="API Error")
        return False