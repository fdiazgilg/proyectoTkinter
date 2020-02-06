from tkinter import *
from tkinter import ttk, Tk, messagebox
import math
import configparser
import sqlite3
import json
import requests
from datetime import datetime

#Lectura del fichero de configuración config.py
config = configparser.ConfigParser()
config.read('config.py')

#Variables clave
DATABASE = './data/{}'.format(config.get('PRODUCTION', 'DB_FILE'))
APIKEY = config.get('PRODUCTION', 'SECRET_KEY')

#Constantes
_WIDTHFRAME = 900
_HEIGHTFRAME = 610
_pady = 15
_textTitle = 'Verdana 8 bold'
_textValue = 'Verdana 8'

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
    
    if len(rows) == 1:
        rows = rows[0]
    elif len(rows) == 0:
        rows = None
    
    conn.commit()
    conn.close()

    return rows


#Clase Marco Movimientos Criptomonedas
class Movements(ttk.Frame):
    headers = ['Date', 'Time', 'From', 'Q', 'To', 'Q', 'U.P.']

    def __init__(self, parent):
        ttk.Frame.__init__(self, height=240, width=_WIDTHFRAME)

        self.pack_propagate(0)
      
        #Cargamos las cabeceras de la tabla de movimientos
        for i in range (0, 7):
            self.lblHead = ttk.Label(self, text=self.headers[i], font=_textTitle, width=14, borderwidth=2, relief='groove', anchor=CENTER)
            self.lblHead.grid(row=0, column=i)
            self.lblHead.grid_propagate(0)

        #Creamos el frame para los movimientos
        self.frameMoves = ttk.Frame(self, height=220, width=812, relief='groove', borderwidth=0)
        self.frameMoves.grid(row=1, column=0, columnspan=7)
        self.frameMoves.grid_propagate(0)
        
        #Creamos el scrollbar
        self.scrollMoves = ttk.Scrollbar(self)
        self.scrollMoves.grid(row=1, column=8)

        #Obtenemos los movimientos de la BD
        self.recordsDB = self.getRecordsDB()
        #Verificamos si la BD tiene movimientos a tratar
        if self.recordsDB != None:
            #Tratamos los movimientos de la BD
            self.dataDB = self.loadMoves(self.recordsDB)
            #Mostramos los movimientos en el frame
            self.printMoves(self.dataDB)

    #Obtenemos los registros de la BD
    def getRecordsDB(self):
        query = """
        SELECT * FROM movements;
        """
        movesDB = dbQuery(query)

        return movesDB
    
    #Cargamos los registros de la BD en una lista de listas
    def loadMoves(self, moves):
        #Si sólo hay un registro, lo convertimos en lista
        if isinstance(moves, dict):
            moves = [moves]
        records = len(moves)
        data = []
        for i in range(records):
            data.append([])
            date = moves[i]['date']
            data[i].append(date)
            time = moves[i]['time']
            data[i].append(time)
            idFrom = moves[i]['from_currency']
            nameFrom = self.nameCrypto(idFrom)
            data[i].append(nameFrom)
            QFrom = moves[i]['from_quantity']
            normalizeQFrom = self.isFloat(QFrom)
            data[i].append(normalizeQFrom)
            idTo = moves[i]['to_currency']
            nameTo = self.nameCrypto(idTo)
            data[i].append(nameTo)
            QTo = moves[i]['to_quantity']
            normalizeQTo = self.isFloat(QTo)
            data[i].append(normalizeQTo)
            PU = QFrom/QTo
            normalizePU = self.isFloat(PU)
            data[i].append(normalizePU)

        return data

    #Mostramos los registros de la BD en la aplicación
    def printMoves(self, data):
        for row in range(len(data)):
            for col in range(len(data[row])):
                value = data[row][col]
                self.lblValue = ttk.Label(self.frameMoves, text=value, font=_textValue, width=16, borderwidth=1, relief='groove', anchor=CENTER)
                self.lblValue.grid(row=row, column=col)

    #Verificación de float separando parte entera y decimal para mostrar correctamente
    def isFloat(self, value):
        dec, ent = math.modf(value)
        if dec == 0:
            res = int(value)
        else:
            res = round(float(value), 5)
        
        return res

    #Obtenemos el nombre de la criptomoneda a partir del id
    def nameCrypto(self, id):
        query = """
        SELECT name FROM cryptos WHERE id = ?;
        """
        crypto = dbQuery(query, id)
        nameCrypto = crypto.get('name')

        return nameCrypto


#Clase Frame Nueva Transacción
class Transaction(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=200, width=_WIDTHFRAME)
        self.simul = parent

        self.pack_propagate(0)

        #Creamos variables de control
        self.valCrypFrom = StringVar()
        self.valCrypTo = StringVar()
        self.valQFrom = StringVar()
        self.valQFrom.set('0')
        self.valQTo = StringVar()
        self.valPU = StringVar()

        #Creamos el frame con tu texto
        self.lblFrame = ttk.Label(self, text='New Transaction', font=_textTitle)
        self.frameNew = ttk.LabelFrame(self, labelwidget=self.lblFrame, borderwidth=2, height=180, width=812, relief='groove')
        self.frameNew.grid(row=0, column=0, columnspan=7)
        self.frameNew.grid_propagate(0)

        #Creamos la etiqueta FROM con su combo
        self.lblFrom = ttk.Label(self.frameNew, text='From:', font=_textTitle, width=12, anchor=E)
        self.lblFrom.grid(row=0, column=0, padx=15, pady=_pady)
        self.lblFrom.grid_propagate(0)

        self.comboFrom = ttk.Combobox(self.frameNew, justify=CENTER, textvariable=self.valCrypFrom, width=22)
        self.comboFrom.grid(row=0, column=1, pady=_pady)
        self.comboFrom.grid_propagate(0)

        #Cargamos los valores del combo FROM
        self.listCombo = self.listCrypto()
        self.comboFrom['values'] = self.listCombo
        self.comboFrom.bind('<<ComboboxSelected>>', self.selCombo)
        
        #Creamos la etiqueta Q_FROM con su caja de texto
        self.lblQfrom = ttk.Label(self.frameNew, text='Q:', font=_textTitle, width=12, anchor=E)
        self.lblQfrom.grid(row=1, column=0, padx=15)
        self.lblQfrom.grid_propagate(0)

        self.boxQfrom = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valQFrom, width=25)
        self.boxQfrom.grid(row=1, column=1)
        self.boxQfrom.grid_propagate(0)

        #Creamos la etiqueta TO con su combo
        self.lblTo = ttk.Label(self.frameNew, text='To:', font=_textTitle, width=15, anchor=E)
        self.lblTo.grid(row=0, column=2, padx=15)
        self.lblTo.grid_propagate(0)

        self.comboTo = ttk.Combobox(self.frameNew, justify=CENTER, textvariable=self.valCrypTo, width=22)
        self.comboTo.grid(row=0, column=3)
        self.comboTo.grid_propagate(0)
        
        #Cargamos los valores del combo TO
        self.comboTo['values'] = self.listCombo
        self.comboTo.bind('<<ComboboxSelected>>', self.selCombo)

        #Creamos la etiqueta Q_TO con su caja de texto
        self.lblQto = ttk.Label(self.frameNew, text='Q:', font=_textTitle, width=15, anchor=E)
        self.lblQto.grid(row=1, column=2, padx=15)
        self.lblQto.grid_propagate(0)
    
        self.boxQto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valQTo, width=25)
        self.boxQto.grid(row=1, column=3)
        self.boxQto.grid_propagate(0)

        #Creamos la etiqueta PU con su caja de texto
        self.lblPUto = ttk.Label(self.frameNew, text='U.P.:', font=_textTitle, width=15, anchor=E)
        self.lblPUto.grid(row=2, column=2, padx=15, pady=_pady)
        self.lblPUto.grid_propagate(0)

        self.boxPUto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valPU, width=25)
        self.boxPUto.grid(row=2, column=3, pady=_pady)
        self.boxPUto.grid_propagate(0)

        #Creamos el botón Aceptar
        self.buttonAcep = ttk.Button(self.frameNew, text='Accept', command=lambda: self.insertBD())
        self.buttonAcep.grid(row=0, column=4, padx=80)
        self.buttonAcep.grid_propagate(0)

        #Creamos el botón Comprobar
        self.buttonCheck = ttk.Button(self.frameNew, text='Check', command=lambda: self.checkTrans())
        self.buttonCheck.grid(row=1, column=4, padx=80)
        self.buttonCheck.grid_propagate(0)

        #Creamos el botón Cancelar
        self.buttonCanc = ttk.Button(self.frameNew, text='Cancel', command=lambda: self.resetValues())
        self.buttonCanc.grid(row=2, column=4, padx=80)
        self.buttonCanc.grid_propagate(0)
    
    #Creamos una lista con los nombres de las criptomonedas
    def listCrypto(self):
        query = """
        SELECT * FROM cryptos;
        """
        cryptos = dbQuery(query)
        listCrypName = []
        for item in cryptos:
            name = item.get('name')
            listCrypName.append(name)
        listCrypName.sort()

        return listCrypName
    
    #Activamos los botones Comprobar y Cancelar al seleccionar un elemento del combo
    def selCombo(self, event):
        self.buttonCheck.configure(state=NORMAL)
        self.buttonCanc.configure(state=NORMAL)

    #Obtenemos el símbolo a partir del nombre de la criptomoneda
    def symbolCryp(self, name):
        query = """
        SELECT symbol FROM cryptos WHERE name = ?;
        """
        crypto = dbQuery(query, name)
        symbCrypto = crypto.get('symbol')

        return symbCrypto

    #Obtenemos el id a partir del símbolo de la criptomoneda
    def idCrypto(self, name):
        query = """
        SELECT id FROM cryptos WHERE symbol = ?;
        """
        crypto = dbQuery(query, name)
        idCrypto = crypto.get('id')

        return idCrypto

    #Inicializamos tras pulsar el botón Cancelar
    def resetValues(self):
        self.valQFrom.set('0')
        self.valCrypFrom.set('')
        self.valCrypTo.set('')
        self.valQTo.set('')
        self.valPU.set('')
        self.buttonAcep.configure(state=DISABLED)
        self.buttonCheck.configure(state=DISABLED)
        self.buttonCanc.configure(state=DISABLED)

    #Acciones tras pulsar el botón Comprobar
    def checkTrans(self):
        validateCrypto = self.validateCombos()
        if validateCrypto:
            validateQFrom = self.validateQFrom()
            if validateQFrom:
                self.convRate = self.priceConv(self.valQFrDB, self.symbolFrom, self.symbolTo)
                self.calcQTO(self.convRate)
                self.calcPU(self.convRate)
                self.buttonAcep.configure(state=NORMAL)

    #Validamos que los combos tengan valores seleccionados y sean distintos entre ellos
    def validateCombos(self):
        if self.valCrypFrom.get() == '':
            messagebox.showwarning(message="Select a From Combo value.", title="Warning")
            return False
        if self.valCrypTo.get() == '':
            messagebox.showwarning(message="Select a To Combo value.", title="Warning")
            return False
        if self.valCrypFrom.get() == self.valCrypTo.get():
            messagebox.showwarning(message="Selected values must be different.", title="Warning")
            return False
        
        #Obtenemos los símbolos de las dos criptomonedas
        self.symbolFrom = self.symbolCryp(self.valCrypFrom.get())
        self.symbolTo = self.symbolCryp(self.valCrypTo.get())

        return True
    
    #Validamos que el valor del campo Q FROM sea numérico y mayor que cero
    def validateQFrom(self):
        #Eliminamos los espacios por la derecha y lo volvemos a pintar en el Entry
        self.valQFrDB = self.valQFrom.get().rstrip()
        self.valQFrom.set(self.valQFrDB)
        try:
            if float(self.valQFrDB) and float(self.valQFrDB) > 0:
                return True
            else:
                messagebox.showwarning(message="Q Entry value must be a number greater than zero.", title="Warning")
                return False
        except:
            messagebox.showwarning(message="Q Entry value must be a number greater than zero.", title="Warning")
            return False
    
    #Invocamos al API para realizar la conversión indicando los valores necesarios
    def priceConv(self, valueQ, cryptoFR, cryptoTO):
        try:
            resp = requests.get("""https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}""".format(valueQ, cryptoFR, cryptoTO, APIKEY))
            if not resp.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(resp)
            js = resp.text
            response = json.loads(js)
            values = response.get('data')
            quote = values['quote']
            conver = quote[cryptoTO]
            rate = conver['price']
            return rate
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)

    #Calculamos el valor de entry Q_TO
    def calcQTO(self, rate):
        #Redondeamos tasa conversión y mostramos en pantalla
        roundRate = round(rate, 5)
        self.valQTo.set(roundRate)

    #Calculamos el valor de entry PU
    def calcPU(self, rate):
        #Asignamos tasa conversión a Q_TO
        self.valQtoDB = rate
        #Calculamos PU, lo redondeamos y mostramos en pantalla
        valuePU = float(self.valQFrDB)/float(self.valQtoDB)
        valuePU = round(valuePU, 5)
        self.valPU.set(valuePU)

    #Acciones tras pulsar el botón Aceptar
    def insertBD(self):
        self.addMoveDB()
        self.simul.updateMove()

    #Añadimos el movimiento a la DB
    def addMoveDB(self):
        #Calculamos fecha y hora con el formato adecuado
        self.getFx()
        #Obtenemos los id de las dos criptomonedas
        self.idFrom = self.idCrypto(self.symbolFrom)
        self.idTo = self.idCrypto(self.symbolTo)

        query = """
        INSERT INTO movements (date, time, from_currency, from_quantity, to_currency, to_quantity)
                    VALUES (?, ?, ?, ?, ?, ?);
        """
        dbQuery(query, self.date, self.time, self.idFrom, self.valQFrDB, self.idTo, self.valQtoDB)
        
    #Obtenemos la fecha y hora actual para realizar el insert
    def getFx(self):
        today = datetime.now()
        formatDate = "%d-%b-%Y" 
        formatTime = "%H:%M"
        self.date = today.strftime(formatDate)
        self.time = today.strftime(formatTime)


#Clase Frame Estado de la inversión
class Status(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, width=812, height=100)

        self.pack_propagate(0)

        #Creamos la etiqueta € Invertidos con su caja de texto
        self.lblInversion = ttk.Label(self, text='Invested €:', font=_textTitle, width=12, anchor=E)
        self.lblInversion.grid(row=0, column=0, padx=15, pady=_pady)
        self.lblInversion.grid_propagate(0)

        self.boxInversion = ttk.Entry(self, justify=RIGHT, width=25, state='readonly')
        self.boxInversion.grid(row=0, column=1)
        self.boxInversion.grid_propagate(0)

        #Creamos la etiqueta Valor Actual con su caja de texto
        self.lblActValue = ttk.Label(self, text='Current value:', font=_textTitle, width=15, anchor=E)
        self.lblActValue.grid(row=0, column=2, padx=15)
        self.lblActValue.grid_propagate(0)

        self.boxValue = ttk.Entry(self, justify=RIGHT, width=25, state='readonly')
        self.boxValue.grid(row=0, column=3)
        self.boxValue.grid_propagate(0)

        #Creamos el botón Calcular
        self.buttonCalc = ttk.Button(self, text='Calculate', command=lambda: self.checkEarn())
        self.buttonCalc.grid(row=0, column=4, padx=80)
        self.buttonCalc.grid_propagate(0)


#Clase Frame Simulador Inversión Criptomonedas
class Investments(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=600, width=_WIDTHFRAME)

        #Verificamos si la tabla MONEDAS de la DATABASE está vacía
        self.checkCrypto()

        #Colocamos el botón '+'
        self.buttonAdd = ttk.Button(self, text ='+', command=lambda: self.stateFrame(self.listWidget, 'readonly'), width=3)
        self.buttonAdd.place(x=860, y=40)

        #Colocamos el frame de los movimientos de criptomonedas
        self.moves = Movements(self)
        self.moves.place(x=20, y=20)

        #Colocamos el frame de la nueva transacción
        self.newTrans = Transaction(self)
        self.newTrans.place(x=20, y=280)
        #Obtenemos la lista de widgets del frame
        self.listWidget = self.newTrans.frameNew.winfo_children()

        #Colocamos el frame del estado de la inversión
        self.statusSimul = Status(self)
        self.statusSimul.place(x=20, y=500)

        #Deshabilitamos el frame de la nueva transacción
        self.stateFrame(self.listWidget, DISABLED)

        #Mostramos ventana de info con las instrucciones
        messagebox.showinfo(message=
        """Steps to simulate a cryptocurrency investment:
        1. Click on '+' button
        2. Select a From Combo value
        3. Select a To Combo value
        4. Both values must be different
        5. Enter a number greater than zero in Q Entry
        6. Click on Check button to fix the data
        7. Click on Accept button to record to the DB""", title="Instructions")

    #Cargamos los movimientos en el frame e inicializamos el área Nueva Transacción
    def updateMove(self):
        self.movesDB = self.moves.getRecordsDB()
        if self.movesDB != None:
            self.data = self.moves.loadMoves(self.movesDB)
            self.moves.printMoves(self.data)
            self.newTrans.resetValues()

    #Función que verifica si la tabla MONEDAS tiene información
    def checkCrypto(self):
        query = """
        SELECT * FROM cryptos;
        """

        cryptos = dbQuery(query)
        if cryptos == None:
            #Cargamos la tabla MONEDAS si está vacía
            self.loadCrypto()

    #Función que carga la tabla MONEDAS
    def loadCrypto(self):
        try:
            resp = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={}&symbol=BTC,ETH,XRP,LTC,BCH,BNB,USDT,EOS,BSV,XLM,ADA,TRX'.format(APIKEY))
            if not resp.status_code // 100 == 2:
                return "Error: Unexpected response {}".format(resp)
            js = resp.text
            response = json.loads(js)
            values = response.get('data')
            #Añadimos las criptomonedas obtenidas en la consulta
            for item in values:
                name = item.get('name')
                symbol = item.get('symbol')

                query = """
                INSERT INTO cryptos (symbol, name)
                            VALUES (?, ?);
                """
                dbQuery(query, symbol, name)

            #Añadimos la moneda Euro y su símbolo
            name = 'Euro'
            symbol = 'EUR'
            query = """
            INSERT INTO cryptos (symbol, name)
                        VALUES (?, ?);
            """
            dbQuery(query, symbol, name)
        
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)

    #Función que cambia el estado de los widgets de un frame
    def stateFrame(self, listChild, status):
        for child in listChild:
            child.configure(state=status)
        if status == 'readonly':
            self.newTrans.boxQfrom.configure(state=NORMAL)
            self.newTrans.buttonAcep.configure(state=DISABLED)
            self.newTrans.buttonCheck.configure(state=DISABLED)
            self.newTrans.buttonCanc.configure(state=DISABLED)
