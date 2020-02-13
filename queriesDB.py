import configparser
import sqlite3
from tkinter import messagebox

#Lectura del fichero de configuración config.py
config = configparser.ConfigParser()
config.read('config.ini')

#Variables clave
DATABASE = './data/{}'.format(config.get('PRODUCTION', 'DB_FILE'))

#Función Consulta DATABASE
def dict_factory(cursor, row):
    d = {}
    for ix, col in enumerate(cursor.description):
        d[col[0]] = row[ix]
    return d

def dbQuery(consulta, *args):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    rows = cursor.execute(consulta, args).fetchall()
    
    conn.commit()
    conn.close()

    return rows


#Obtenemos los registros de la tabla MOVIMIENTOS
#Esta query nos da la lista de registro de MOVIMIENTOS cargar la aplicación (lineas 76 - 698)
#Las consultas en lineas 302 - 464 sólo son para verificar que existen movimientos
#PODRIAMOS PRESCINDIR DE NAMECRYPTO LINEAS 96 - 103
#SELECT b.date, b.time, a.name, b.from_quantity, c.name, b.to_quantity FROM cryptos a INNER JOIN (cryptos c INNER JOIN movements b ON c.id = b.to_currency) ON a.id = b.from_currency;
'''
def getRecordsDB():
    query = """
    SELECT b.date, b.time, a.name, b.from_quantity, c.name, b.to_quantity FROM cryptos a INNER JOIN(cryptos c INNER JOIN movements b ON c.id = b.to_currency) ON a.id = b.from_currency ORDER BY b.id;
    """
    movesDB = dbQuery(query)
    print(movesDB)

    return movesDB
'''

def getRecordsDB():
    query = """
    SELECT date, time, from_currency, from_quantity, to_currency, to_quantity FROM movements
    ORDER BY id;
    """
    movesDB = dbQuery(query)

    return movesDB

#Obtenemos el número de registros de la tabla MONEDAS
def cryptos():
    query = """
    SELECT count(id) FROM cryptos;
    """
    cryptos = dbQuery(query)

    return cryptos

#Obtenemos la lista ordenada de los nombres de la tabla MONEDAS
def names():
    query = """
    SELECT name FROM cryptos
    ORDER BY name;
    """
    names = dbQuery(query)

    return names

#Obtenemos el símbolo a partir del nombre de la criptomoneda
def symbolCryp(name):
    query = """
    SELECT symbol FROM cryptos WHERE name = ?;
    """
    symbol = dbQuery(query, name)

    return symbol

#Obtenemos el id a partir del símbolo de la criptomoneda
def idCrypto(name):
    query = """
    SELECT id FROM cryptos WHERE symbol = ?;
    """
    ind = dbQuery(query, name)

    return ind

#Obtenemos el nombre de la criptomoneda a partir del id
def nameCrypto(ind):
    query = """
    SELECT name FROM cryptos WHERE id = ?;
    """
    name = dbQuery(query, ind)

    return name

#Obtenemos el nombre de la criptomoneda a partir del símbolo
def nameBalance(symbol):
    query = """
    SELECT name FROM cryptos WHERE symbol = ?;
    """
    name = dbQuery(query, symbol)

    return name

#Realizamos el insert en la tabla de movimientos
def insertDB(date, time, idFrom, qFrom, idTo, qTo):
    query = """
    INSERT INTO movements (date, time, from_currency, from_quantity, to_currency, to_quantity)
                VALUES (?, ?, ?, ?, ?, ?);
    """
    dbQuery(query, date, time, idFrom, qFrom, idTo, qTo)


#Realizamos el insert en la tabla de criptomonedas
def insertCrypto(cryptos):
    query = """
    INSERT INTO cryptos (symbol, name)
                VALUES (?, ?);
    """
    for item in cryptos:
        dbQuery(query, item[0], item[1])

#Obtenemos la cantidad FROM de una criptomoneda
def investedCrypto(symbol):
    query = """
    SELECT from_quantity FROM cryptos a INNER JOIN 
    movements b ON a.id = b.from_currency WHERE a.symbol = ?;
    """
    invCrypto = dbQuery(query, symbol)

    return invCrypto

#Obtenemos la cantidad TO de una criptomoneda
def returnedCrypto(symbol):
    query = """
    SELECT to_quantity FROM cryptos a INNER JOIN 
    movements b ON a.id = b.to_currency WHERE a.symbol = ?;
    """
    retCrypto = dbQuery(query, symbol)

    return retCrypto

#Obtenemos la lista de las criptomonedas en las que hemos invertido
def toCrypto():
    query = """
    SELECT DISTINCT symbol, name FROM movements a INNER JOIN 
    cryptos b ON a.to_currency = b.id;
    """
    retToCrypto = dbQuery(query)

    return retToCrypto