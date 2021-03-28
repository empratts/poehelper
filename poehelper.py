#Main driver for PoEHelper
from settings import Settings
from api import API
from ui import UserInterface
from chaos import Chaos
from inventory import Inventory
from tkinter import Tk, N, Button
import requests

def main():

    def gracefulExit():
        ui.killAllThreads()
        root.destroy()
    
    stgs = Settings()
    stgs.writeSettings()

    root = Tk()

    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.wm_overrideredirect(True)
    root.wm_overrideredirect(1)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "white")
    root.config(bg='white')

    inv = Inventory()
    api = API()
    chaos = Chaos(stgs, inv)

    ui = UserInterface(root, stgs, inv, api, chaos)

    Button(root, text="Quit", command = gracefulExit, anchor=N).place(x=root.winfo_screenwidth()/2, y=root.winfo_screenheight()-30)

    root.mainloop()

main()