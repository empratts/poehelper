from tkinter import Tk, Canvas, Frame, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED
from functools import partial
import time

class Overlay(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.master.title("Overlay Frame")
        self.pack(fill=BOTH, expand=1)

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
        print("Open Options Menu")

