#Main driver for PoEHelper
from settings import Settings
from api import API
from ui import UserInterface
from chaos import Chaos
from log import ReadLogFile
from inventory import Inventory
from tkinter import Tk, N, Button
import requests

def main():

    def gracefulExit():
        ui.killAllThreads()
        root.destroy()
    
    settings = Settings()
    settings.writeSettings()

    root = Tk()

    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.wm_overrideredirect(True)
    root.wm_overrideredirect(1)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "white")
    root.config(bg='white')

    
    api = API(settings)
    log = ReadLogFile(root, settings)

    log.reopenLogfile()

    inv = Inventory(settings, api)
    chaos = Chaos(settings, inv, log)

    ui = UserInterface(root, settings, inv, api, chaos, log)

    Button(root, text="Quit", command = gracefulExit, anchor=N).place(x=root.winfo_screenwidth()/2, y=root.winfo_screenheight()-30)

    root.mainloop()

main()