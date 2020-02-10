from tkinter import *
from tkinter import ttk, messagebox
import utilities
import api
import queriesDB

#Constantes
_WIDTHFRAME = 900
_HEIGHTFRAME = 610
_pady = 15
_textTitle = 'Verdana 8 bold'
_textValue = 'Verdana 8'


#Clase Marco Movimientos Criptomonedas
class Movements(ttk.Frame):
    headers = ['Date', 'Time', 'From', 'Q', 'To', 'Q', 'U.P.']

    def __init__(self, parent):
        ttk.Frame.__init__(self, height=240, width=_WIDTHFRAME)
        
        self.simul = parent

        #Añadimos las cabeceras de la tabla
        self.loadHeaders()

        #Añadimos el container para el canvas y el scroll
        self.container = ttk.Frame(self, borderwidth=2, width=810, height=220, relief='groove')
        self.container.grid(column=0, row=1, columnspan=8)
        
        #Añadimos el scrollbar
        self.scroll = ttk.Scrollbar(self.container)
        self.scroll.grid(column=1, row=0, sticky=N+S)
        self.scroll.grid_columnconfigure(1, weight=1)
        
        #Añadimos el canvas
        self.canvas = Canvas(self.container, yscrollcommand=self.scroll.set)
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        self.canvas.configure(width=810, height=220)
        self.canvas.grid_propagate(0)
        self.scroll.config(command=self.canvas.yview)

        #Añadimos el frame scrollable    
        self.frameMoves = ttk.Frame(self.canvas, width=810, height=220)
        
        #Comprobamos si tenemos movimientos
        self.checkMoves()
        
        #Creamos la ventana denro del canvas con el frame scrollable
        self.windows=self.canvas.create_window((0, 0), anchor=NW, window=self.frameMoves)
        
        #Actualizamos la región del canvas
        self.frameMoves.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    #Cargamos las cabeceras de la tabla de movimientos
    def loadHeaders(self):
        for i in range (0, 7):
            self.lblHead = ttk.Label(self, text=self.headers[i], font=_textTitle, width=14, relief='groove', anchor=CENTER)
            self.lblHead.grid(row=0, column=i)
            self.lblHead.grid_propagate(0)
        #Añadimos otro "hueco" para cuadrar con el scroll
        self.lblHead = ttk.Label(self, font=_textTitle, width=2)
        self.lblHead.grid(row=0, column=7)
        self.lblHead.grid_propagate(0)
    
    #Verificamos si tenemos movimientos en la BD
    def checkMoves(self):
        #Obtenemos los movimientos de la BD
        self.recordsDB = queriesDB.getRecordsDB()
        #Verificamos si la BD tiene movimientos a tratar
        if self.recordsDB != None:
            #Tratamos los movimientos de la BD
            self.dataDB = self.loadMoves(self.recordsDB)
            #Mostramos los movimientos en el frame
            self.printMoves(self.dataDB)

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
            nameFrom = queriesDB.nameCrypto(idFrom)
            data[i].append(nameFrom)
            QFrom = moves[i]['from_quantity']
            #Verificamos si es float o int
            normalizeQFrom = utilities.isFloat(QFrom, 5)
            data[i].append(normalizeQFrom)
            idTo = moves[i]['to_currency']
            nameTo = queriesDB.nameCrypto(idTo)
            data[i].append(nameTo)
            QTo = moves[i]['to_quantity']
            #Verificamos si es float o int
            normalizeQTo = utilities.isFloat(QTo, 5)
            data[i].append(normalizeQTo)
            PU = QFrom/QTo
            #Verificamos si es float o int
            normalizePU = utilities.isFloat(PU,5 )
            data[i].append(normalizePU)

        return data

    #Mostramos los registros de la BD en la aplicación
    def printMoves(self, data):
        for row in range(len(data)):
            for col in range(len(data[row])):
                value = data[row][col]
                self.lblValue = ttk.Label(self.frameMoves, text=value, font=_textValue, width=16, borderwidth=0, relief='groove', anchor=CENTER)
                self.lblValue.grid(row=row, column=col)
        self.canvas.config(scrollregion= self.canvas.bbox('all'))

    def refreshScroll(self):
        #Actualizamos el frame scrollable para que muestre el último movimiento
        self.frameMoves.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox('all'))        
      

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
        self.frameNew = ttk.LabelFrame(self, labelwidget=self.lblFrame, borderwidth=0, height=180, width=812, relief='groove')
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
        self.listCombo = self.cryptoName(self.simul.listCrypCoins)
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
    
        self.boxQto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valQTo, width=25, background='white')
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

        #Creamos el botón Convertir
        self.buttonConvert = ttk.Button(self.frameNew, text='Convert', command=lambda: self.conversion())
        self.buttonConvert.grid(row=1, column=4, padx=80)
        self.buttonConvert.grid_propagate(0)

        #Creamos el botón Cancelar
        self.buttonCanc = ttk.Button(self.frameNew, text='Cancel', command=lambda: self.resetValues())
        self.buttonCanc.grid(row=2, column=4, padx=80)
        self.buttonCanc.grid_propagate(0)
    
    def cryptoName(self, values):
        listCrypName = []
        for item in values:
            name = item.get('name')
            listCrypName.append(name)
        listCrypName.sort()

        return listCrypName
    
    #Activamos los botones Convertir y Cancelar al seleccionar un elemento del combo
    def selCombo(self, event):
        self.buttonConvert.configure(state=NORMAL)
        self.buttonCanc.configure(state=NORMAL)

    #Inicializamos tras pulsar el botón Cancelar
    def resetValues(self):
        self.valQFrom.set('0')
        self.valCrypFrom.set('')
        self.valCrypTo.set('')
        self.valQTo.set('')
        self.valPU.set('')
        self.buttonAcep.configure(state=DISABLED)
        self.buttonConvert.configure(state=DISABLED)
        self.buttonCanc.configure(state=DISABLED)

    #Acciones tras pulsar el botón Convertir
    def conversion(self):
        #Obtenemos la lista de movimientos de la BD
        self.records = queriesDB.getRecordsDB()
        #Obtenemos la lista de criptomonedas en la columna TO
        self.listCryptoTo, self.listCrypNameTo = queriesDB.toCrypto()
        #Añadimos el Euro porque siempre puede elegirse en el FROM
        self.listCrypNameTo.append('Euro')
        print(self.listCrypNameTo)
        #Calculamos la cantidad total (invertido - retornado) de cada criptomoneda
        self.totalCryptoTO = self.totalCrypto(self.listCryptoTo)
        print(self.totalCryptoTO)
        validateCrypto = self.validateCombos()
        if validateCrypto:
            validateQFrom = self.validateQFrom()
            if validateQFrom:
                self.convRate = api.priceConv(self.valQFrDB, self.symbolFrom, self.symbolTo)
                #Si tenemos precio de conversión continuamos con la transacción
                if self.convRate:
                    self.calcQTO(self.convRate)
                    self.calcPU(self.convRate)
                    self.buttonAcep.configure(state=NORMAL)

    #Validamos que los combos tengan valores seleccionados y sean distintos entre ellos
    def validateCombos(self):
        if self.valCrypFrom.get() == '':
            messagebox.showwarning(message="Select a From Combo value.", title="Warning")
            return False
        #La primera inversión SIEMPRE debe ser en Euros
        elif self.valCrypFrom.get() != 'Euro' and self.records == None:
            messagebox.showwarning(message="From Combo value must be Euro.", title="Warning")
            return False
        #Si ya tenemos registros, FROM puede ser en Euros o en las criptomonedas que tengamos en TO
        elif self.records != None and self.valCrypFrom.get() not in self.listCrypNameTo:
            messagebox.showwarning(message="From Combo value must be Euro or a Crypto in column TO.", title="Warning")
            return False
        if self.valCrypTo.get() == '':
            messagebox.showwarning(message="Select a To Combo value.", title="Warning")
            return False
        if self.valCrypFrom.get() == self.valCrypTo.get():
            messagebox.showwarning(message="Selected values must be different.", title="Warning")
            return False
        
        #Obtenemos los símbolos de las dos criptomonedas
        self.symbolFrom = queriesDB.symbolCryp(self.valCrypFrom.get())
        self.symbolTo = queriesDB.symbolCryp(self.valCrypTo.get())

        return True
    
    #Validamos que el valor del campo Q FROM sea numérico y mayor que cero
    def validateQFrom(self):
        #Eliminamos los espacios por la derecha y lo volvemos a pintar en el Entry
        self.valQFrDB = self.valQFrom.get().rstrip()
        self.valQFrom.set(self.valQFrDB)
        for item in self.totalCryptoTO:
            if item[0] == self.symbolFrom:
                maxValue = item[1]
                print(maxValue)
        try:
            if float(self.valQFrDB) and float(self.valQFrDB) > 0 and float(self.valQFrDB) <= maxValue:
                return True
            elif float(self.valQFrDB) > maxValue:
                messagebox.showwarning(message=
                """Q Entry value must be a number less than {}.""".format(utilities.isFloat(maxValue, 5)), title="Warning")
                return False
            else:
                messagebox.showwarning(message=
                """Q Entry value must be a number greater than zero.""", title="Warning")
                return False
        except:
            messagebox.showwarning(message=
            """Q Entry value must be a number.""", title="Warning")
            return False

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
        messagebox.showinfo(message="Record added successfully.", title="Info")

    #Añadimos el movimiento a la DB
    def addMoveDB(self):
        #Calculamos fecha y hora con el formato adecuado
        self.date, self.time = utilities.getFx()
        #Obtenemos los id de las dos criptomonedas
        self.idFrom = queriesDB.idCrypto(self.symbolFrom)
        self.idTo = queriesDB.idCrypto(self.symbolTo)
        queriesDB.insertDB(self.date, self.time, self.idFrom, self.valQFrDB, self.idTo, self.valQtoDB)

    #Calculamos el total de cada criptomoneda, invertido - retornado
    def totalCrypto(self, cryptos):
        totCrypto = []
        for symbol in cryptos:
            returnedCrypto = 0
            investedCrypto = 0
            ret = queriesDB.returnedCrypto(symbol)
            #Si no hay ningún registro continuamos
            if ret != None:
            #Si sólo hay un registro, lo convertimos en lista
                if isinstance(ret, dict):
                    ret = [ret]

                for row in ret:
                    returnedCrypto += row['to_quantity']

            inv = queriesDB.investedCrypto(symbol)
            #Si no hay ningún registro continuamos
            if inv != None:
            #Si sólo hay un registro, lo convertimos en lista
                if isinstance(inv, dict):
                    inv = [inv]

                for row in inv:
                    investedCrypto += row['from_quantity']

            if (returnedCrypto - investedCrypto) != 0:
                totCrypto.append((symbol, returnedCrypto - investedCrypto))
            
        return totCrypto


#Clase Frame Estado de la inversión
class Status(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, width=812, height=100)

        self.pack_propagate(0)

        #Creamos variables de control
        self.investedEuros = StringVar()
        self.currentValue = StringVar()

        #Creamos la etiqueta € Invertidos con su caja de texto
        self.lblInversion = ttk.Label(self, text='Invested €:', font=_textTitle, width=12, anchor=E)
        self.lblInversion.grid(row=0, column=0, padx=15, pady=_pady)
        self.lblInversion.grid_propagate(0)

        self.boxInversion = ttk.Entry(self, justify=RIGHT, width=25, textvariable=self.investedEuros, state='readonly')
        self.boxInversion.grid(row=0, column=1)
        self.boxInversion.grid_propagate(0)

        #Creamos la etiqueta Valor Actual con su caja de texto
        self.lblActValue = ttk.Label(self, text='Current value:', font=_textTitle, width=15, anchor=E)
        self.lblActValue.grid(row=0, column=2, padx=15)
        self.lblActValue.grid_propagate(0)

        self.boxValue = ttk.Entry(self, justify=RIGHT, width=25, textvariable=self.currentValue, state='readonly')
        self.boxValue.grid(row=0, column=3)
        self.boxValue.grid_propagate(0)

        #Creamos el botón Calcular
        self.buttonCalc = ttk.Button(self, text='Calculate', command=lambda: self.investState())
        self.buttonCalc.grid(row=0, column=4, padx=80)
        self.buttonCalc.grid_propagate(0)

    #Calculamos el estado de la inversión
    def investState(self):
        #Lista de símbolos de las criptomonedas
        cryptos = queriesDB.symbols()

        #Lista de movimientos de la tabla movimientos
        moves = queriesDB.getRecordsDB()

        #Si no tenemos movimientos seteamos a cero los Entry
        if moves == None:
            self.investedEuros.set('0')
            self.currentValue.set('0')
        
        else:
            #Inicializamos el sumatorio en euros de las criptomonedas
            totalCrypEuros = 0

            #Recorremos la lista de criptomonedas
            for item in cryptos:
                symbol = item['symbol']
                #Inicializamos los valores de criptomonedas invertidas y retornadas
                investedCrypto = 0
                returnedCrypto = 0
                investedEuro = 0
                returnedEuro = 0
                if symbol != 'EUR':
                    #Cálculo de criptomonedas invertidas
                    fromRowsCrypto = queriesDB.investedCrypto(symbol)

                    #Si no hay ningún registro continuamos
                    if fromRowsCrypto != None:
                        #Si sólo hay un registro, lo convertimos en lista
                        if isinstance(fromRowsCrypto, dict):
                            fromRowsCrypto = [fromRowsCrypto]
                        investedCrypto = 0
                        for row in fromRowsCrypto:
                            investedCrypto += row['from_quantity']

                    #Cálculo de criptomonedas retornadas
                    toRowsCrypto = queriesDB.returnedCrypto(symbol)
                    
                    #Si no hay ningún registro continuamos
                    if toRowsCrypto != None:
                        #Si sólo hay un registro, lo convertimos en lista
                        if isinstance(toRowsCrypto, dict):
                            toRowsCrypto = [toRowsCrypto]

                        returnedCrypto = 0
                        for row in toRowsCrypto:
                            returnedCrypto += row['to_quantity']

                    #Calculamos la diferencia entre las criptomonedas invertidas y las retornadas
                    totalCrypto = investedCrypto - returnedCrypto

                    #Si la cantidad de criptomonedas es mayor que cero las convertimos y las sumamos al total
                    if totalCrypto > 0:
                        #Invocamos al API para realizar la conversión indicando los valores necesarios
                        totalCrypEuros += api.priceConv(totalCrypto, symbol, 'EUR')
                    #Si la cantidad de criptomonedas es menor que cero la convertimos y restamos del total
                    elif totalCrypto < 0:
                        totalCrypto *= -1
                        #Invocamos al API para realizar la conversión indicando los valores necesarios
                        totalCrypEuros -= api.priceConv(totalCrypto, symbol, 'EUR')

                #Si el símbolo es el euro no necesitamos invocar al API para realizar la conversión
                else:        
                    #Cálculo de € invertidos
                    fromRows = queriesDB.investedCrypto('EUR')

                    #Si sólo hay un registro, lo convertimos en lista
                    if isinstance(fromRows, dict):
                        fromRows = [fromRows]

                    invested = 0
                    for row in fromRows:
                        investedEuro += row['from_quantity']
                    
                    #Cálculo de € retornados
                    toRows = queriesDB.returnedCrypto('EUR')

                    #Si no hay ningún registro continuamos
                    if toRows != None:
                        #Si sólo hay un registro, lo convertimos en lista
                        if isinstance(toRows, dict):
                            toRows = [toRows]

                        returned = 0
                        for row in toRows:
                            returnedEuro += row['to_quantity']

                    #Calculamos la diferencia entre los € invertidos y los retornados
                    totalEuro = investedEuro - returnedEuro
                    #Redondeamos y cambiamos el '.' por la ','
                    totalEuro = utilities.isFloat(totalEuro, 2)

                    #Seteamos la variable de control para mostrar el valor en el Entry Inversión
                    self.investedEuros.set(totalEuro)
                
            #Redondeamos y cambiamos el '.' por la ','
            totalCrypEuros = utilities.isFloat(totalCrypEuros, 2)
            #Seteamos la variable de control para mostrar el valor en el Entry Valor Actual
            self.currentValue.set(totalCrypEuros)


#Clase Frame Simulador Inversión Criptomonedas
class Investments(ttk.Frame):
    listCrypCoins = []
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=600, width=_WIDTHFRAME)

        #Verificamos si la tabla MONEDAS de la DATABASE está vacía
        self.checkCryptoTable()

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

    #Ventana de información con las instrucciones para invertir
    def instructions(self):
        messagebox.showinfo(message=
        """Steps to simulate a cryptocurrency investment:
        1. Click on '+' button
        2. Select a From Combo value
        3. Select a To Combo value
        4. Both values must be different
        5. Enter a number greater than zero in Q Entry
        6. Click on Convert button to fix the data
        7. Click on Accept button to record to the DB""", title="Instructions")

    #Cargamos los movimientos en el frame e inicializamos el área Nueva Transacción
    def updateMove(self):
        self.movesDB = queriesDB.getRecordsDB()
        if self.movesDB != None:
            self.data = self.moves.loadMoves(self.movesDB)
            self.moves.printMoves(self.data)
            self.moves.refreshScroll()
            self.newTrans.resetValues()
        

    #Función que verifica si la tabla MONEDAS tiene información
    def checkCryptoTable(self):
        cryptos = queriesDB.cryptos()
        if cryptos == None:
            #Si la tabla MONEDAS está vacía obtenemos las criptomonedas de la API
            cryptoApi = api.getCrypto()
            #Con los valores recibidos del API creamos una lista de tuplas
            cryptoValues = []
            for item in cryptoApi:
                crypto = (item.get('symbol'), item.get('name'))
                cryptoValues.append(crypto)
            
            #Ahora añadimos a esa lista la moneda €
            euro = ('EUR', 'Euro')
            cryptoValues.append(euro)
            #Insertamos en la tabla de monedas
            queriesDB.insertCrypto(cryptoValues)
        
        #Obtenemos la lista de criptomonedas para luego cargar los combos
        self.listCrypCoins = queriesDB.cryptos()

    #Función que cambia el estado de los widgets de un frame
    def stateFrame(self, listChild, status):
        for child in listChild:
            child.configure(state=status)
        if status == 'readonly':
            self.newTrans.boxQfrom.configure(state=NORMAL)
            self.newTrans.buttonAcep.configure(state=DISABLED)
            self.newTrans.buttonConvert.configure(state=DISABLED)
            self.newTrans.buttonCanc.configure(state=DISABLED)