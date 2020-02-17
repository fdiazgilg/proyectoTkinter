import configparser
import sqlite3
from tkinter import messagebox


#Lectura del fichero de configuración config.ini
config = configparser.ConfigParser()
config.read('config.ini')

#Variables clave
DATABASE = './data/{}'.format(config.get('PRODUCTION', 'DB_FILE'))


#Definición dbQuery
def dbQuery(consulta, *args):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    rows = cursor.execute(consulta, args).fetchall()
    
    conn.commit()
    conn.close()

    return rows


#Obtenemos los registros de la tabla MOVIMIENTOS
def getRecordsDB():
    query = """
    SELECT b.date, b.time, a.name, b.from_quantity, c.name, b.to_quantity FROM cryptos a 
    INNER JOIN(cryptos c INNER JOIN movements b ON c.id = b.to_currency) ON a.id = b.from_currency 
    ORDER BY b.id;
    """
    movesDB = dbQuery(query)

    return movesDB


#Obtenemos el número de registros de la tabla MONEDAS
def cryptos():
    query = """
    SELECT count(*) FROM cryptos;
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


#Obtenemos el símbolo y el id a partir del nombre de la criptomoneda
def symbolIdCryp(name):
    query = """
    SELECT symbol, id FROM cryptos WHERE name = ?;
    """
    symbolId = dbQuery(query, name)

    return symbolId


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
    cryptos b ON a.to_currency = b.id
    ORDER BY name;
    """
    retToCrypto = dbQuery(query)

    return retToCrypto