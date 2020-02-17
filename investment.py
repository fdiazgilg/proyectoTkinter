from tkinter import *
from tkinter import ttk, messagebox
import utilities
import apiCoin
import queriesDB
import sqlite3
import sys


#Constantes
_WIDTHFRAME = 900
_widthframe = 360
_HEIGHTFRAME = 610
_heightframe = 235
_pady = 15
_padx = 80
_textTitle = 'Verdana 8 bold'
_textValue = 'Verdana 8'
_invLimit = 1000000


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

        #Creamos la ventana dentro del canvas con el frame scrollable
        self.windows=self.canvas.create_window((0, 0), anchor=NW, window=self.frameMoves)
        
        #Comprobamos si tenemos movimientos
        self.checkMoves()

        #Actualizamos la región si hay movimientos
        if len(self.recordsDB) != 0:
            self.frameMoves.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))


    #Cargamos las cabeceras de la tabla de movimientos
    def loadHeaders(self):
        for i in range (0, 7):
            self.lblHead = ttk.Label(self, text=self.headers[i], font=_textTitle, width=14, relief='sunken', anchor=CENTER)
            self.lblHead.grid(row=0, column=i)
            self.lblHead.grid_propagate(0)
        #Añadimos otro "hueco" para cuadrar con el scroll
        self.lblHead = ttk.Label(self, font=_textTitle, width=2)
        self.lblHead.grid(row=0, column=7)
        self.lblHead.grid_propagate(0)
    

    #Verificamos si tenemos movimientos en la BD
    def checkMoves(self):
        #Obtenemos los movimientos de la BD
        try:
            self.recordsDB = queriesDB.getRecordsDB()
        except sqlite3.Error as e:
            messagebox.showerror(message="Error DB: {}".format(e), title="SQLite Error")
        #Verificamos si la BD tiene movimientos a tratar
        if len(self.recordsDB) != 0:
            #Tratamos los movimientos de la BD
            self.dataDB = self.loadMoves(self.recordsDB)
            #Mostramos los movimientos en el frame
            self.printMoves(self.dataDB)


    #Cargamos los registros de la BD en una lista de listas y los tratamos
    def loadMoves(self, moves):
        records = len(moves)
        data = []
        for i in range(records):
            data.append([])
            date = moves[i][0]
            data[i].append(date)
            time = moves[i][1]
            data[i].append(time)
            nameFrom = moves[i][2]
            data[i].append(nameFrom)
            QFrom = moves[i][3]
            #Verificamos si es float o int
            normalizeQFrom = utilities.isFloat(QFrom, 5)
            data[i].append(normalizeQFrom)
            nameTo = moves[i][4]
            data[i].append(nameTo)
            QTo = moves[i][5]
            #Verificamos si es float o int
            normalizeQTo = utilities.isFloat(QTo, 5)
            data[i].append(normalizeQTo)
            PU = QFrom/QTo
            #Verificamos si es float o int
            normalizePU = utilities.isFloat(PU, 5)
            data[i].append(normalizePU)

        return data


    #Mostramos los registros de la BD en la aplicación
    def printMoves(self, data):
        for row in range(len(data)):
            for col in range(len(data[row])):
                value = data[row][col]
                self.lblValue = ttk.Label(self.frameMoves, text=value, font=_textValue, width=16, borderwidth=0, relief='groove', anchor=CENTER)
                self.lblValue.grid(row=row, column=col)
                self.lblValue.grid_propagate(0)


    #Actualizamos el frame scrollable para que muestre el último movimiento
    def refreshScroll(self):
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

        self.comboFrom = ttk.Combobox(self.frameNew, justify=CENTER, textvariable=self.valCrypFrom, width=17, postcommand=self.refreshCombo)
        self.comboFrom.grid(row=0, column=1, pady=_pady)
        self.comboFrom.grid_propagate(0)

        #Cargamos los valores del combo FROM de forma dinámica
        self.refreshCombo()
        self.comboFrom.bind('<<ComboboxSelected>>', self.selCombo)
        
        #Creamos la etiqueta Q_FROM con su caja de texto
        self.lblQfrom = ttk.Label(self.frameNew, text='Q:', font=_textTitle, width=12, anchor=E)
        self.lblQfrom.grid(row=1, column=0, padx=15)
        self.lblQfrom.grid_propagate(0)

        self.boxQfrom = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valQFrom, width=20)
        self.boxQfrom.grid(row=1, column=1)
        self.boxQfrom.grid_propagate(0)

        #Creamos la etiqueta TO con su combo
        self.lblTo = ttk.Label(self.frameNew, text='To:', font=_textTitle, width=18, anchor=E)
        self.lblTo.grid(row=0, column=2, padx=15)
        self.lblTo.grid_propagate(0)

        self.comboTo = ttk.Combobox(self.frameNew, justify=CENTER, textvariable=self.valCrypTo, width=17)
        self.comboTo.grid(row=0, column=3)
        self.comboTo.grid_propagate(0)
        
        #Cargamos los valores del combo TO
        self.loadComboTo()

        #Creamos la etiqueta Q_TO con su caja de texto
        self.lblQto = ttk.Label(self.frameNew, text='Q:', font=_textTitle, width=18, anchor=E)
        self.lblQto.grid(row=1, column=2, padx=15)
        self.lblQto.grid_propagate(0)
    
        self.boxQto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valQTo, width=20, background='white')
        self.boxQto.grid(row=1, column=3)
        self.boxQto.grid_propagate(0)

        #Creamos la etiqueta PU con su caja de texto
        self.lblPUto = ttk.Label(self.frameNew, text='U.P.:', font=_textTitle, width=18, anchor=E)
        self.lblPUto.grid(row=2, column=2, padx=15, pady=_pady)
        self.lblPUto.grid_propagate(0)

        self.boxPUto = ttk.Entry(self.frameNew, justify=RIGHT, textvariable=self.valPU, width=20)
        self.boxPUto.grid(row=2, column=3, pady=_pady)
        self.boxPUto.grid_propagate(0)

        #Creamos el botón Aceptar
        self.buttonAcep = ttk.Button(self.frameNew, text='Accept', command=lambda: self.insertBD())
        self.buttonAcep.grid(row=0, column=4, padx=_padx)
        self.buttonAcep.grid_propagate(0)

        #Creamos el botón Convertir
        self.buttonConvert = ttk.Button(self.frameNew, text='Convert', command=lambda: self.conversion())
        self.buttonConvert.grid(row=1, column=4, padx=_padx)
        self.buttonConvert.grid_propagate(0)

        #Creamos el botón Cancelar
        self.buttonCanc = ttk.Button(self.frameNew, text='Cancel', command=lambda: self.resetValues())
        self.buttonCanc.grid(row=2, column=4, padx=_padx)
        self.buttonCanc.grid_propagate(0)


    #Refrescamos los valores del combo FROM
    def refreshCombo(self):
        #Obtenemos la lista de criptomonedas en la columna TO
        listCrypto = queriesDB.toCrypto()
        self.listCryptoTo = []
        for i in range(len(listCrypto)):
            self.listCryptoTo.append(listCrypto[i][0])
        #Calculamos la cantidad total (invertido - retornado) de cada criptomoneda
        self.totalCryptoTO = self.totalCrypto(self.listCryptoTo)
        #Sólo mostramos las cryptos con cantidad distinta de 0
        self.listCombo = self.loadName(self.totalCryptoTO)
        self.comboFrom['values'] = self.listCombo


    #Obtenemos la lista de criptomonedas a mostrar en el combo FROM
    def loadName(self, dataBalance):
        listFrom = []
        for item in dataBalance:
            nameCrypto = queriesDB.nameBalance(item[0])
            name = nameCrypto[0][0]
            quantity = item[1]
            #Sólo mostramos en el balance las criptomonedas con cantidad mayor que 0.00001
            if quantity > 0.00001:
                listFrom.append(name)
        #Añadimos el Euro si no está en la lista y ordenamos
        if 'Euro' not in listFrom:
            listFrom.append('Euro')
        listFrom.sort()

        return listFrom


    #Calculamos el total de cada criptomoneda, invertido - retornado
    def totalCrypto(self, cryptos):
        totCrypto = []
        for symbol in cryptos:
            #Obtenemos el sumatorio total de cada criptomoneda
            totalCrypto = self.simul.sumCrypto(symbol)

            if totalCrypto != 0:
                #Obtenemos una lista de tuplas con el símbolo y la cantidad de cada criptomoneda
                totCrypto.append((symbol, totalCrypto))

        return totCrypto


    #Cargamos los valores del combo TO
    def loadComboTo(self):
        namesTo = queriesDB.names()
        self.listComboTo = []
        for item in namesTo:
            self.listComboTo.append(item[0])
        self.comboTo['values'] = self.listComboTo
        self.comboTo.bind('<<ComboboxSelected>>', self.selCombo)


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
        #Invocamos a la función de validación de los valores de los combos
        validateCrypto = self.validateCombos()
        if validateCrypto:
            #Invocamos a la función de validación de los valores de Q_FROM
            validateQFrom = self.validateQFrom()
            if validateQFrom:
                self.convRate = apiCoin.priceConv(self.symbolFrom, self.symbolTo)
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
        if self.valCrypTo.get() == '':
            messagebox.showwarning(message="Select a To Combo value.", title="Warning")
            return False
        if self.valCrypFrom.get() == self.valCrypTo.get():
            messagebox.showwarning(message="Selected values must be different.", title="Warning")
            return False
        
        #Obtenemos los símbolos y los ids de las dos criptomonedas
        symbolIdFrom = queriesDB.symbolIdCryp(self.valCrypFrom.get())
        self.symbolFrom = symbolIdFrom[0][0]
        self.idFrom = symbolIdFrom[0][1]
        symbolIdTo = queriesDB.symbolIdCryp(self.valCrypTo.get())
        self.symbolTo = symbolIdTo[0][0]
        self.idTo = symbolIdTo[0][1]

        return True


    #Validamos que el valor del campo Q FROM sea numérico y mayor que cero
    def validateQFrom(self):
        #Eliminamos los espacios por la derecha y lo volvemos a pintar en el Entry
        self.valQFrDB = self.valQFrom.get().rstrip()
        self.valQFrom.set(self.valQFrDB)
        if len(self.records) != 0:
            for item in self.totalCryptoTO:
                if item[0] == self.symbolFrom:
                    maxValue = item[1]
        try:
            if self.symbolFrom != 'EUR':
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
            else:
                if float(self.valQFrDB) and float(self.valQFrDB) > 0 and float(self.valQFrDB) <= _invLimit:
                    return True
                elif float(self.valQFrDB) > _invLimit:
                    messagebox.showwarning(message=
                    """Q Entry value must be a number less than {}€.""".format(utilities.isFloat(_invLimit, 5)), title="Warning")
                    return False
                else:
                    messagebox.showwarning(message=
                    """Q Entry value must be a number greater than zero.""", title="Warning")
                    return False

        except:
            messagebox.showwarning(message=
            """Q Entry value must be a number.""", title="Warning")
            return False


    #Calculamos el valor de Entry Q_TO
    def calcQTO(self, rate):
        #Convertimos en float el valor de Entry Q_FROM
        self.valQFrDB = float(self.valQFrDB)
        #Multiplicamos la tasa de conversión por la cantidad del Entry Q_FROM
        self.valQToDB = rate * self.valQFrDB
        #Redondeamos el resultado
        roundRate = round(self.valQToDB, 5)
        self.valQTo.set(roundRate)


    #Calculamos el valor de Entry PU
    def calcPU(self, rate):
        #Calculamos PU, lo redondeamos y mostramos en pantalla
        valuePU = self.valQFrDB/self.valQToDB
        valuePU = round(valuePU, 5)
        self.valPU.set(valuePU)


    #Acciones tras pulsar el botón Aceptar
    def insertBD(self):
        try:
            self.addMoveDB()
            self.simul.updateTable()
            messagebox.showinfo(message="Record added successfully.", title="Info")
        except sqlite3.Error as e:
            messagebox.showerror(message="Error DB: {}".format(e), title="SQLite Error")


    #Añadimos el movimiento a la DB
    def addMoveDB(self):
        #Calculamos fecha y hora con el formato adecuado
        self.date, self.time = utilities.getFx()
        queriesDB.insertDB(self.date, self.time, self.idFrom, self.valQFrDB, self.idTo, self.valQToDB)



#Clase Frame Estado de la inversión
class Status(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, width=812, height=100)
        self.simul = parent

        self.pack_propagate(0)

        #Creamos variables de control
        self.investedEuros = StringVar()
        self.currentValue = StringVar()
        self.profits = StringVar()

        #Creamos la etiqueta € Invertidos con su caja de texto
        self.lblInversion = ttk.Label(self, text='Investment:', font=_textTitle, width=12, anchor=E)
        self.lblInversion.grid(row=0, column=0, padx=15, pady=_pady)
        self.lblInversion.grid_propagate(0)

        self.boxInversion = ttk.Entry(self, justify=RIGHT, width=20, textvariable=self.investedEuros, state='readonly', background='white')
        self.boxInversion.grid(row=0, column=1)
        self.boxInversion.grid_propagate(0)

        #Creamos la etiqueta Valor Actual con su caja de texto
        self.lblActValue = ttk.Label(self, text='Current value Crypto:', font=_textTitle, width=18, anchor=E)
        self.lblActValue.grid(row=0, column=2, padx=15)
        self.lblActValue.grid_propagate(0)

        self.boxValue = ttk.Entry(self, justify=RIGHT, width=20, textvariable=self.currentValue, state='readonly')
        self.boxValue.grid(row=0, column=3)
        self.boxValue.grid_propagate(0)

        #Creamos el botón Calcular
        self.buttonCalc = ttk.Button(self, text='Calculate', command=lambda: self.investState())
        self.buttonCalc.grid(row=0, column=4, padx=_padx)
        self.buttonCalc.grid_propagate(0)

        #Creamos la etiqueta Beneficio con su caja de texto
        self.lblActValue = ttk.Label(self, text='Profits:', font=_textTitle, width=18, anchor=E)
        self.lblActValue.grid(row=1, column=2, padx=15)
        self.lblActValue.grid_propagate(0)

        self.boxValue = ttk.Entry(self, justify=RIGHT, width=20, textvariable=self.profits, state='readonly')
        self.boxValue.grid(row=1, column=3)
        self.boxValue.grid_propagate(0)

        #Creamos el botón Balance
        self.buttonBal = ttk.Button(self, text='Balance', command=lambda: self.balance(), state=DISABLED)
        self.buttonBal.grid(row=1, column=4, padx=_padx)
        self.buttonBal.grid_propagate(0)


    #Calculamos el estado de la inversión
    def investState(self):
        #Lista de movimientos de la tabla movimientos
        moves = queriesDB.getRecordsDB()
        #Inicializamos el Entry de beneficios
        self.profits.set('')

        #Si no tenemos movimientos seteamos a cero los Entry
        if len(moves) == 0:
            self.investedEuros.set('0€')
            self.currentValue.set('0€')
            self.totalBalance = 0
            
            #Mensaje para indicar que los cálculos han finalizado
            messagebox.showinfo(message="Calculated successfully", title="Info")
            
            #Activamos el botón Balance
            self.buttonBal.configure(state=NORMAL)
       
        else:
            #Lista de símbolos de las criptomonedas en el TO
            cryptosTO = queriesDB.toCrypto()
            listCryptos = []
            for i in range(len(cryptosTO)):
                listCryptos.append(cryptosTO[i][0])
            #Eliminamos el Euro, si existe, porque no tenemos que invocar a la API
            if 'EUR' in listCryptos:
                listCryptos.remove('EUR')

            #Inicializamos el sumatorio en euros de las criptomonedas
            totalCrypEuros = 0
            #Inicializamos la lista para el Balance
            self.totalBalance = []
            #Recorremos la lista de criptomonedas en el TO
            for symbol in listCryptos:

                #Obtenemos el sumatorio total de cada criptomoneda
                totalCrypto = self.simul.sumCrypto(symbol)

                #Creamos una lista de tuplas para mostrar en Balance
                cryptoBalance = (symbol, totalCrypto)
                self.totalBalance.append(cryptoBalance)

                #Si la cantidad de criptomonedas es distinta de cero las convertimos y las sumamos al total
                if totalCrypto != 0:
                    #Invocamos al API para realizar la conversión indicando los valores necesarios
                    rate = apiCoin.priceConv(symbol, 'EUR')
                    subTotal = rate * totalCrypto
                    totalCrypEuros += subTotal

            #Si no hay error API continuamos con los cálculos
            if rate != False:

                #Obtenemos el sumatorio total de cada criptomoneda
                totalEuro = self.simul.sumCrypto('EUR')
                
                #Si obtenemos beneficios, mostramos 0€ en la inversión y mostramos los beneficios en otro Entry
                if totalEuro < 0:
                    invEur = '0€'
                    totalEuro = utilities.isFloat(-totalEuro, 2)
                    totalEuro = str(totalEuro) + '€'
                    self.profits.set(totalEuro)
                else:
                    #Redondeamos y cambiamos el '.' por la ','
                    totalEuro = utilities.isFloat(totalEuro, 2)
                    invEur = str(totalEuro) + '€'

                #Seteamos la variable de control para mostrar el valor en el Entry Inversión
                self.investedEuros.set(invEur)
                
                #Redondeamos y cambiamos el '.' por la ','
                totalCrypEuros = utilities.isFloat(totalCrypEuros, 2)
                #Si la cantidad en € de las criptomonedas, una vez redondeada, es cercana a 0, seteamos a cero el Entry
                if totalCrypEuros == '0,0':
                    curVal = '0€'
                else:
                    curVal = str(totalCrypEuros) + '€'
                #Seteamos la variable de control para mostrar el valor en el Entry Valor Actual
                self.currentValue.set(curVal)
        
                #Mensaje para indicar que los cálculos han finalizado
                messagebox.showinfo(message="Calculated successfully", title="Info")
                
                #Activamos el botón Balance
                self.buttonBal.configure(state=NORMAL)


    #Ventana para mostrar el balance de criptomonedas
    def balance(self):
        #Obtenemos los datos del balance de la invocación anterior en Calcular
        dataBalance = self.totalBalance

        #Deshabilitamos los botones Calcular y Balance al pulsar Balance
        self.buttonCalc.configure(state=DISABLED)
        self.buttonBal.configure(state=DISABLED)

        #Si no tenemos movimientos en la BD mostramos un mensaje y habilitamos Calcular
        if dataBalance == 0:
            messagebox.showwarning(message="There are no cryptocurrencies.", title="Balance Investments")
            self.buttonCalc.configure(state=NORMAL)

        else:
            #Tratamos los datos del balance obtenido anteriormente para guardarlo en la lista
            listBalance = self.loadBalance(dataBalance)

            if listBalance != []:
                #Si existen movimientos creamos una ventana para mostrar el balance
                self.createBalWindow()

                #Cabeceras de la tabla balance
                self.balanceHeaders = ['Cryptocurrency', 'Quantity', 'Current Value']

                #Cargamos las cabeceras de la tabla de balance
                for i in range(len(self.balanceHeaders)):
                    self.lblHead = ttk.Label(self.cryptoBal, text=self.balanceHeaders[i], font=_textTitle, width=14, relief='ridge', anchor=CENTER)
                    self.lblHead.grid(row=0, column=i, pady=3)
                    self.lblHead.grid_propagate(0)

                #Mostramos los datos en la tabla de balance
                for row in range(len(listBalance)):
                    for col in range(len(listBalance[row])):
                        value = listBalance[row][col]
                        self.lblValue = ttk.Label(self.cryptoBal, text=value, font=_textValue, width=16, relief='groove', anchor=CENTER)
                        self.lblValue.grid(row=row+1, column=col, padx=2)
                        self.lblValue.grid_propagate(0)
            
            else:
                self.buttonCalc.configure(state=NORMAL)


    #Creamos una ventana para mostrar el balance
    def createBalWindow(self):
        self.cryptoBal = Toplevel()
        self.cryptoBal.title('Balance Investments')

        #Controlamos el cierre de la ventana de balance
        self.cryptoBal.protocol("WM_DELETE_WINDOW", self.closeBalance)

        #Calculamos ancho y alto de nuestra pantalla
        self.ws = self.winfo_screenwidth()
        self.hs = self.winfo_screenheight()

        #Fijamos las coordinadas x e y para centrar la ventana
        self.cryptoBal.posx = int((self.ws/2) - (_widthframe/2))
        self.cryptoBal.posy = int((self.hs/2) - (_heightframe/2))

        #Posicionamos la pantalla y evitamos que se pueda cambiar de tamaño
        self.cryptoBal.geometry("{}x{}+{}+{}".format(_widthframe, _heightframe, self.cryptoBal.posx, self.cryptoBal.posy))
        self.cryptoBal.resizable(0, 0)

        #Provocamos que la ventana hija transite con la padre
        self.cryptoBal.transient(self.simul)


    #Calculamos el formato a presentar en la ventana balance
    def loadBalance(self, dataBalance):
        listBalance = []
        for item in dataBalance:
            nameCrypto = queriesDB.nameBalance(item[0])
            name = nameCrypto[0][0]
            quantity = item[1]
            if quantity > 0.00001:
                quantityNorm = utilities.isFloat(quantity, 5)
                symbol = item[0]
                rate = apiCoin.priceConv(symbol, 'EUR')
                if rate:
                    value = rate * float(quantity)
                    valueNorm = utilities.isFloat(value, 2)
                    valueNorm = str(valueNorm) + '€'
                    data = (name, quantityNorm, valueNorm)
                    listBalance.append(data)

        return listBalance


    #Función para controlar el cierre de la ventana de balance
    def closeBalance(self):
        answer = messagebox.askokcancel(message="Do you want to close the balance?", title="Balance Cryptocurrencies")
        if answer:
            self.cryptoBal.destroy()
            #Al cerrar la ventana balance activamos de nuevo el botón Calcular
            self.buttonCalc.configure(state=NORMAL)



#Clase Frame Simulador Inversión Criptomonedas
class Investments(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, height=600, width=_WIDTHFRAME)

        #Verificamos si la tabla MONEDAS de la BD está vacía
        try:
            self.checkCryptoTable()
        except sqlite3.Error as e:
            messagebox.showerror(message="Error DB: {}".format(e), title="SQLite Error")
            sys.exit()

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
    7. Click on Accept button to record to the DB
    8. Click on Calculate to get the balance
    9. Click on Balance to know the amount of cryptocurrencies""", title="Instructions")


    #Cargamos los movimientos en el frame e inicializamos el área Nueva Transacción
    def updateTable(self):
        self.movesDB = queriesDB.getRecordsDB()
        if len(self.movesDB) != 0:
            self.data = self.moves.loadMoves(self.movesDB)
            self.moves.printMoves(self.data)
            self.moves.refreshScroll()
            self.newTrans.resetValues()
        

    #Función que verifica si la tabla MONEDAS tiene información
    def checkCryptoTable(self):
        cryptos = queriesDB.cryptos()
        regNum = cryptos[0][0]
        if regNum == 0:
            #Si la tabla MONEDAS está vacía obtenemos las criptomonedas de la API
            cryptoApi = apiCoin.getCrypto()
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
        

    #Función que cambia el estado de los widgets de un frame
    def stateFrame(self, listChild, status):
        for child in listChild:
            child.configure(state=status)
        if status == 'readonly':
            self.newTrans.boxQfrom.configure(state=NORMAL)
            self.newTrans.buttonAcep.configure(state=DISABLED)
            self.newTrans.buttonConvert.configure(state=DISABLED)
            self.newTrans.buttonCanc.configure(state=DISABLED)

    
    #Obtenemos el sumatorio total de cada criptomoneda
    def sumCrypto(self, symbol):
        #Calculo la cantidad de criptomoneda retornada
        returnCrypto = queriesDB.returnedCrypto(symbol)
        
        #Calculo la cantidad de criptomoneda invertida
        investCrypto = queriesDB.investedCrypto(symbol)

        #Si no tenemos valor, inicializamos a 0 y en caso contrario le asignamos el valor
        if returnCrypto[0][0] == None:
            returnCrypto = 0
        else:
            returnCrypto = returnCrypto[0][0]

        #Si no tenemos valor, inicializamos a 0 y en caso contrario le asignamos el valor
        if investCrypto[0][0] == None:
            investCrypto = 0
        else:
            investCrypto = investCrypto[0][0]

        #Obtenemos el total, pero en el caso de los Euros restamos al revés
        if symbol == 'EUR':
            totalCrypto = investCrypto - returnCrypto
        else:
            totalCrypto = returnCrypto - investCrypto

        return totalCrypto