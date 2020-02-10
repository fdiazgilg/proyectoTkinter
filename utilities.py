#Librería de utilidades
import math
from datetime import datetime


#Verificación de float separando parte entera y decimal y cambiando '.' por ',' si es float, para mostrar correctamente
#También recibe por parámetro el valor de redondeo
def isFloat(value, roundVal):
    dec, ent = math.modf(value)
    if dec == 0:
        res = int(value)
    else:
        res = round(float(value), roundVal)

    if isinstance(res, float):
        res = str(res).replace('.', ',')
    
    return res

#Obtenemos la fecha y hora actual para realizar el insert
def getFx():
    today = datetime.now()
    formatDate = "%d-%b-%Y" 
    formatTime = "%H:%M"
    date = today.strftime(formatDate)
    time = today.strftime(formatTime)

    return date, time