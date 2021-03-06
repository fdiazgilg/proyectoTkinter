#Librería de utilidades
import math
import locale
from datetime import datetime

#Establecemos configuración numérica local
locale.setlocale(locale.LC_NUMERIC, '')


#Verificación de float separando parte entera y decimal y utilizando locale
#También recibe por parámetro el número de decimales a fijar
#Para los € mostramos 2 decimales y para el resto de valores 8
def isFloat(value, roundVal):
    dec, ent = math.modf(value)
    if dec == 0:
        res = locale.format('%.0f', value, grouping=True)
    elif roundVal == 8:
        res = locale.format('%.8f', value, grouping=True).rstrip('0')
        #Si la longitud supera las doce posiciones, prescindimos de la parte decimal
        if len(res) > 12:
            res = locale.format('%.0f', value, grouping=True)
    elif roundVal == 2:
        res = locale.format('%.2f', value, grouping=True)
    #Caso especial para mostrar el valor límite del Q_FROM
    else:
        res = locale.format('%.8f', value, grouping=True).rstrip('0')
    #Excepción. Al realizar rstrip podríamos quedarnos con un valor 0,
    if res == '0,':
        res = 0

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
    dictApiErr = {400:'Bad Request', 401:'Unauthorized', 402:'Payment Required', 403:'Forbbiden', 429:'Too Many Requests', 500:'Internal Server Error'}
    if error == 400 or error == 500:
        ret = "HTTP Error Code {}: {}".format(error, dictApiErr.get(error))
    else:
        ret = "HTTP Error Code {}: {} - {}".format(error, dictApiErr.get(error), message)
    
    return ret