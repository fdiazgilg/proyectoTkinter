#Librería de utilidades
import math
from datetime import datetime


#Verificación de float separando parte entera y decimal y cambiando '.' por ',' para mostrarlo correctamente
#También recibe por parámetro el número de decimales a fijar
def isFloat(value, roundVal):
    dec, ent = math.modf(value)
    if dec == 0:
        res = format(int(value), ',.0f')
    elif roundVal == 5:
        res = format(value, ',.5f').rstrip('0')
        #Excepción para mostrar el valor correctamente
        if res == '0.':
            res = '0.00000'
    else:
        res = format(value, ',.2f').rstrip('0')
        #Excepción para mostrar el valor correctamente
        if res == '0.':
            res = '0.00'
    
    res = res.replace(',', '@').replace('.', ',').replace('@', '.')
    
    return res


#Obtenemos la fecha y hora actual para realizar el insert
def getFx():
    today = datetime.now()
    formatDate = "%d-%b-%Y" 
    formatTime = "%H:%M"
    date = today.strftime(formatDate)
    time = today.strftime(formatTime)

    return date, time


#Gestión de errores de la API
def apiErrors(error, response):
    message = response['status']['error_message']

    if error == 400:
        ret = "HTTP Error Code {}: Bad Request".format(error)
    if error == 401:
        ret = "HTTP Error Code {}: Unauthorized - {}".format(error, message)
    if error == 402:
        ret = "HTTP Error Code {}: Payment Required - {}".format(error, message)
    if error == 403:
        ret = "HTTP Error Code {}: Forbbiden - {}".format(error, message)
    if error == 429:
        ret = "HTTP Error Code {}: Too Many Requests - {}".format(error, message)
    if error == 500:
        ret = "HTTP Error Code {}: Internal Server Error".format(error)
    
    return ret