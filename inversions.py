from tkinter import *
from tkinter import ttk, Tk, messagebox
import configparser
import sqlite3
import json
import requests

#Lectura del fichero de configuración config.ini
config = configparser.ConfigParser()
config.read('config.ini')

#Variables clave
DATABASE = './data/{}'.format(config.get('PRODUCTION', 'DB_FILE'))
APIKEY = config.get('PRODUCTION', 'SECRET_KEY')

#Constantes
_WIDTHFRAME = 900

#Funciones Consulta DATABASE
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


#Clase Frame Movimientos Criptomonedas
class Movements(ttk.Frame):
    headers = ['Date', 'Time', 'From', 'Q', 'To', 'Q', 'U.P.']

    def __init__(self, parent):
        ttk.Frame.__init__(self, height=240, width=_WIDTHFRAME)

        self.pack_propagate(0)

        labelStyle = ttk.Style()
        labelStyle.configure('my.TLabel', font='Verdana 10')
        
        #Cargamos las cabeceras de la tabla de movimientos
        for i in range (0, 7):
            self.lblHead = ttk.Label(self, text=self.headers[i], style='my.TLabel', width=14, borderwidth=1, relief='groove', anchor=CENTER)
            self.lblHead.grid(row=0, column=i)
            self.lblHead.grid_propagate(0)
       
        self.frameMovements = ttk.Frame(self, width=812, height=220, relief='groove', borderwidth=1)
        self.frameMovements.grid(row=1, column=0, columnspan=7)

        #self.frameMovements.grid_propagate(0)
        
        self.scrollMovements = ttk.Scrollbar(self)
        self.scrollMovements.grid(row=1, column=8)
        '''
        self.canvas.configure(yscrollcommand=self.scrollMovements.set)

        
        self.canvas = Canvas(self.frameMovements, yscrollcommand=self.scrollMovements.set)
        
        
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        self.canvas.config(width=812, height=180)
        self.canvas.grid_propagate(0)
        self.windows  =self.canvas.create_window(0,0, anchor=NW, window=self.frameMovements)
        '''


#Clase Frame Nueva Transacción
class Transaction(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=200, width=_WIDTHFRAME)

        self.pack_propagate(0)

        self.textQTo = StringVar()
        self.textPU = StringVar()

        labelStyle = ttk.Style()
        labelStyle.configure('my.TLabel', font='Verdana 10')

        buttonStyle = ttk.Style()
        buttonStyle.configure('my.TButton', font='Verdana 10')

        #Creamos el marco con tu texto
        self.lblFrame = ttk.Label(self, text='New Transaction', style='my.TLabel')
        self.frameNew = ttk.LabelFrame(self, labelwidget=self.lblFrame, borderwidth=2, height=180, width=812, relief='groove')
        self.frameNew.grid(row=0, column=0, columnspan=7)
        self.frameNew.grid_propagate(0)

        #Creamos la etiqueta FROM con su combo
        self.lblFrom = ttk.Label(self.frameNew, text='From:', style='my.TLabel', width=12, anchor=E)
        self.lblFrom.grid(row=0, column=0, padx=15, pady=15)
        self.lblFrom.grid_propagate(0)

        self.comboFrom = ttk.Combobox(self.frameNew, justify=CENTER, width=22)
        self.comboFrom.grid(row=0, column=1, pady=15)
        self.comboFrom.grid_propagate(0)
        #Cargamos los valores del combo
        self.listCombo = self.listCryptoCoins()
        self.comboFrom['values'] = self.listCombo
        self.comboFrom.bind('<<ComboboxSelected>>', self.getSelectFrom)
        
        #Creamos la etiqueta Q_FROM con su caja de texto inicializada a cero
        self.lblQfrom = ttk.Label(self.frameNew, text='Q:', style='my.TLabel', width=12, anchor=E)
        self.lblQfrom.grid(row=1, column=0, padx=15)
        self.lblQfrom.grid_propagate(0)

        self.boxQfrom = ttk.Entry(self.frameNew, justify=RIGHT, width=25)
        self.boxQfrom.insert(0,0)
        self.boxQfrom.grid(row=1, column=1)
        self.boxQfrom.grid_propagate(0)

        #Creamos la etiqueta TO con su combo
        self.lblTo = ttk.Label(self.frameNew, text='To:', style='my.TLabel', width=15, anchor=E)
        self.lblTo.grid(row=0, column=2, padx=15)
        self.lblTo.grid_propagate(0)

        self.comboTo = ttk.Combobox(self.frameNew, justify=CENTER, width=22)
        self.comboTo.grid(row=0, column=3)
        self.comboTo.grid_propagate(0)
        #Cargamos los valores del combo
        self.comboTo['values'] = self.listCombo
        self.comboTo.bind('<<ComboboxSelected>>', self.getSelectTo)

        #Creamos la etiqueta Q_TO con su caja de texto
        self.lblQto = ttk.Label(self.frameNew, text='Q:', style='my.TLabel', width=15, anchor=E)
        self.lblQto.grid(row=1, column=2, padx=15)
        self.lblQto.grid_propagate(0)
    
        self.boxQto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.textQTo, width=25)
        self.boxQto.grid(row=1, column=3)
        self.boxQto.grid_propagate(0)

        #Creamos la etiqueta PU con su caja de texto
        self.lblPUto = ttk.Label(self.frameNew, text='U.P.:', style='my.TLabel', width=15, anchor=E)
        self.lblPUto.grid(row=2, column=2, padx=15, pady=15)
        self.lblPUto.grid_propagate(0)

        self.boxPUto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.textPU, width=25)
        self.boxPUto.grid(row=2, column=3, pady=15)
        self.boxPUto.grid_propagate(0)

        #Creamos el botón Aceptar
        self.buttonAcep = ttk.Button(self.frameNew, text='Accept', style='my.TButton', command=lambda: self.checkTrans())
        self.buttonAcep.grid(row=0, column=4, padx=80)
        self.buttonAcep.grid_propagate(0)

        #Creamos el botón Cancelar
        self.buttonCanc = ttk.Button(self.frameNew, text='Cancel', style='my.TButton')
        self.buttonCanc.grid(row=1, column=4, padx=80)
        self.buttonCanc.grid_propagate(0)
    
    #Creamos una lista con las criptomonedas añadiendo el valor Euro
    def listCryptoCoins(self):
        query = """
        SELECT name FROM cryptos;
        """
        cryptos = dbQuery(query)
        listCryptos = []
        for item in cryptos:
            name = item.get('name')
            listCryptos.append(name)
        listCryptos.append('Euro')
        listCryptos.sort()

        return listCryptos
    
    def getSelectFrom(self, event):
        cryptoFrom = self.comboFrom.get()
        if cryptoFrom == '':
            pass
        elif cryptoFrom == 'Euro':
            self.getCryptoFR = 'EUR'
        else:
            self.getCryptoFR = self.symbolCryptoCoins(cryptoFrom)
        print(self.getCryptoFR)

    def getSelectTo(self, event):
        cryptoTo = self.comboTo.get()
        if cryptoTo == '':
            pass
        elif cryptoTo == 'Euro':
            self.getCryptoTO = 'EUR'
        else:
            self.getCryptoTO = self.symbolCryptoCoins(cryptoTo)
        print(self.getCryptoTO)

    #Obtenemos el símbolo a partir del nombre
    def symbolCryptoCoins(self, name):
        query = """
        SELECT symbol FROM cryptos WHERE name = ?;
        """
        crypto = dbQuery(query, name)
        symbolCrypto = crypto.get('symbol')

        return symbolCrypto

    def checkTrans(self):
        self.validateCombos()
        self.validateQFrom()
        self.price = self.conversion(self.valueQFR, self.getCryptoFR, self.getCryptoTO)
        self.valueQTO(self.price)

     
    def validateCombos(self):
        if self.getCryptoFR == '':
            messagebox.showinfo(message="You must select a value from Combo From", title="Warning")
        elif self.getCryptoTO == '':
            messagebox.showinfo(message="You must select a value from Combo To", title="Warning")
        elif self.getCryptoFR == self.getCryptoTO:
            messagebox.showinfo(message="Selected values must be different", title="Warning")
    
    def validateQFrom(self):
        self.valueQFR = self.boxQfrom.get()
        if self.valueQFR.isdigit() and int(self.valueQFR) > 0:
            print(self.valueQFR)
        else:
            messagebox.showinfo(message="You must enter an integer value greater than zero", title="Warning")
        return self.valueQFR
    
    def conversion(self, valueQ, cryptoFR, cryptoTO):
        resp = requests.get('https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY={}'.format(valueQ, cryptoFR, cryptoTO, APIKEY))
        if resp.status_code == 200:
            js = resp.text
            response = json.loads(js)
            values = response.get('data')
            print(values)
            quote = values['quote']
            conver = quote[self.getCryptoTO]
            price = conver['price']
            print(price)

        else:
            print(resp.status_code)
            print(resp)
        return price

    def valueQTO(self, price):
        self.textQTo.set(price)
        self.textPU.set(int(self.valueQFR)/price)
    

#Clase Frame Estado de la inversión
class Status(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, width=812, height=100)

        self.pack_propagate(0)

        labelStyle = ttk.Style()
        labelStyle.configure('my.TLabel', font='Verdana 10')

        buttonStyle = ttk.Style()
        buttonStyle.configure('my.TButton', font='Verdana 10')

        #Creamos la etiqueta € Invertidos con su caja de texto
        self.lblInversion = ttk.Label(self, text='Invested €:', style='my.TLabel', width=12, anchor=E)
        self.lblInversion.grid(row=0, column=0, padx=15, pady=15)
        self.lblInversion.grid_propagate(0)

        self.boxInversion = ttk.Entry(self, justify=RIGHT, width=25)
        self.boxInversion.grid(row=0, column=1)
        self.boxInversion.grid_propagate(0)

        #Creamos la etiqueta Valor Actual con su caja de texto
        self.lblValue = ttk.Label(self, text='Current value:', style='my.TLabel', width=15, anchor=E)
        self.lblValue.grid(row=0, column=2, padx=15)
        self.lblValue.grid_propagate(0)

        self.boxValue = ttk.Entry(self, justify=RIGHT, width=25)
        self.boxValue.grid(row=0, column=3)
        self.boxValue.grid_propagate(0)

        #Creamos el botón Calcular
        self.buttonCalc = ttk.Button(self, text='Calculate', style='my.TButton')
        self.buttonCalc.grid(row=0, column=4, padx=80)
        self.buttonCalc.grid_propagate(0)


#Clase Frame Simulador Inversión Criptomonedas
class Investments(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=600, width=_WIDTHFRAME)

        #Verificamos si la tabla MONEDAS de la DATABASE está vacía
        self.checkCrypto()

        #Colocamos el botón '+'
        self.Button1 = ttk.Button(self, text ='+', command=lambda: self.stateFrame(self.listTrans, 'readonly'), width=3)
        self.Button1.place(x=870, y=40)

        #Colocamos el frame de los movimientos de criptomonedas
        self.moves = Movements(self)
        self.moves.place(x=20, y=20)

        #Colocamos el frame de la nueva transacción
        self.newTrans = Transaction(self)
        self.newTrans.place(x=20, y=280)
        self.listTrans = self.newTrans.frameNew.winfo_children()

        #Colocamos el frame del estado de la inversión
        self.statusInversion = Status(self)
        self.statusInversion.place(x=20, y=500)

        #Deshabilitamos el frame de la nueva transacción
        self.stateFrame(self.listTrans, DISABLED)


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
        resp = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={}&symbol=BTC,ETH,XRP,LTC,BCH,BNB,USDT,EOS,BSV,XLM,ADA,TRX'.format(APIKEY))
        try:
            if resp.status_code == 200:
                js = resp.text
                response = json.loads(js)
                values = response.get('data')
                for item in values:
                    name = item.get('name')
                    symbol = item.get('symbol')

                    query = """
                    INSERT INTO cryptos (symbol, name)
                                VALUES (?, ?);
                    """
                    dbQuery(query, symbol, name)
        except:
            print('El error devuelto por CoinMarketCap es {}'.format(resp.status_code))

    #Función que cambia el estado de los widgets de un frame
    def stateFrame(self, listChild, status):
        for child in listChild:
            child.configure(state=status)
        if status == 'readonly':
            self.newTrans.boxQfrom.configure(state=NORMAL)
