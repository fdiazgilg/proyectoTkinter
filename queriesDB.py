import configparser
import sqlite3
import traceback, sys
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

    try:
        rows = cursor.execute(consulta, args).fetchall()
    except sqlite3.Error as e:
        messagebox.showerror(message="DataBase Error: {}".format(e), title="SQLite Error")
        #traceback.print_exc(file=sys.stdout)
        #return None
    
    if len(rows) == 1:
        rows = rows[0]
    elif len(rows) == 0:
        rows = None
    
    conn.commit()
    conn.close()

    return rows

#Obtenemos los registros de la tabla MOVIMIENTOS
def getRecordsDB():
    query = """
    SELECT * FROM movements;
    """
    movesDB = dbQuery(query)

    return movesDB

#Obtenemos los registros de la tabla MONEDAS
def cryptos():
    query = """
    SELECT * FROM cryptos;
    """
    cryptos = dbQuery(query)

    return cryptos

#Obtenemos los símbolos de la tabla MONEDAS
def symbols():
    query = """
    SELECT symbol FROM cryptos;
    """
    cryptos = dbQuery(query)

    return cryptos

#Obtenemos el símbolo a partir del nombre de la criptomoneda
def symbolCryp(name):
    query = """
    SELECT symbol FROM cryptos WHERE name = ?;
    """
    crypto = dbQuery(query, name)
    symbCrypto = crypto.get('symbol')

    return symbCrypto

#Obtenemos el id a partir del símbolo de la criptomoneda
def idCrypto(name):
    query = """
    SELECT id FROM cryptos WHERE symbol = ?;
    """
    crypto = dbQuery(query, name)
    idCrypto = crypto.get('id')

    return idCrypto

#Obtenemos el nombre de la criptomoneda a partir del id
def nameCrypto(id):
    query = """
    SELECT name FROM cryptos WHERE id = ?;
    """
    crypto = dbQuery(query, id)
    nameCrypto = crypto.get('name')

    return nameCrypto

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
    listretToCrypto = []
    listretToNameCryp = []
    if isinstance(retToCrypto, dict):
        retToCrypto = [retToCrypto]
    for item in retToCrypto:
        listretToCrypto.append(item.get('symbol'))
        listretToNameCryp.append(item.get('name'))

    return listretToCrypto, listretToNameCryp