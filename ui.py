from tkinter import Tk, Canvas, Frame, Toplevel, Label, Entry, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED
from functools import partial
import time
import json

class Overlay(Frame):

    def __init__(self, master, settings):
        super().__init__(master=master)

        self.initUI(settings)

    def initUI(self, settings):

        self.master.title("Overlay Frame")
        self.pack(fill=BOTH, expand=1)
        self.menu = None
        self.settings = settings

        self.x = 23
        self.y = 170

        self.w = 840
        self.h = 840

        self.canvas = Canvas(self, bd=-2)
        self.canvas.config(bg='white')
        self.canvas.pack(fill=BOTH, expand=1)

        self.menuButton = Button(self.canvas, text="Menu", command = self.optionsMenu, anchor=N)
        self.menuButton.place(x=self.winfo_screenwidth()/2 + 20, y=0)

        self.redraw()

    def redraw(self):
        return

    def optionsMenu(self):
        if self.menu == None:
            self.menu = Menu(self.master, self)
        else:
            self.closeMenu()
            print(self.menu)
    
    def closeMenu(self):
        self.menu.destroy()
        self.menu = None

class Menu(Toplevel):

    def __init__(self, master=None, parent=None):
        super().__init__(master=master)

        self.initMenu(parent)

    def initMenu(self, parent):

        self.parent = parent

        self.title("Menu")
        self.geometry("400x600")
        self.protocol("WM_DELETE_WINDOW", self.parent.closeMenu)
        label = Label(self, text="Menu options here")
        label.pack()

        settingsFrame = Frame(self, bg='white')

        settings = self.parent.settings.listSettings()

        i = 0
        self.setEntry = {}
        for k, v in settings.items():

            setLabel = Label(settingsFrame, text=k)
            self.setEntry[k] = Entry(settingsFrame)
            self.setEntry[k].insert(0,json.dumps(v).replace('"',''))
            setLabel.grid(row=i, column=0)
            self.setEntry[k].grid(row=i, column=1)

            i += 1

        settingsFrame.pack()

        save = Button(self,text="Save", command=self.saveAndClose, anchor=N)
        save.pack()

    def saveAndClose(self):
        settings = {}
        for k, v in self.setEntry.items():
            settings[k] = v.get()

        self.parent.settings.modifySettings(settings)

        self.parent.closeMenu()