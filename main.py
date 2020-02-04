from tkinter import *
from tkinter import ttk
from inversions import Investments

class mainApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Crypto Investments')
        self.geometry("{}x{}".format(910, 600))
        self.resizable(0, 0)

        c = Investments(self)
        c.place(x=0, y=0)

    def start(self):
        self.mainloop()

if __name__ == '__main__':
    app = mainApp()
    app.start()