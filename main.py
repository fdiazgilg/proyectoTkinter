from tkinter import *
from tkinter import ttk
from inversions import Investments, _HEIGHTFRAME, _WIDTHFRAME


class mainApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Crypto Investments')

        #Calculamos ancho y alto de nuestra pantalla
        self.ws = self.winfo_screenwidth()
        self.hs = self.winfo_screenheight()

        #Fijamos las coordinadas x e y para centrar la ventana
        self.posx = int((self.ws/2) - (_WIDTHFRAME/2))
        self.posy = int((self.hs/2) - (_HEIGHTFRAME/2))

        self.geometry("{}x{}+{}+{}".format(_WIDTHFRAME, _HEIGHTFRAME, self.posx, self.posy))
        self.resizable(0, 0)

        self.simul = Investments(self)
        self.simul.place(x=0, y=0)

    def start(self):
        self.mainloop()


if __name__ == '__main__':
    app = mainApp()
    app.start()