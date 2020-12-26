#Main driver for PoEHelper
from settings import Settings
from api import RateLimiter
from ui import Overlay
from tkinter import Tk, N, Button
import requests

def main():
    """
    inv = Inventory()
    ui = UI()
    api = API()
    chaos = Chaos()
    s = Settings()

    ui.start()
    """

    

    RL = RateLimiter()
    stgs = Settings()
    stgs.writeSettings()

    root = Tk()

    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.wm_overrideredirect(True)
    root.wm_overrideredirect(1)
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "white")
    root.config(bg='white')

    ui = Overlay(root, stgs)

    Button(root, text="Quit", command = root.destroy, anchor=N).place(x=root.winfo_screenwidth()/2, y=root.winfo_screenheight()-30)
    

    root.mainloop()

    """
    league = stgs.settings["league"]
    accountName = stgs.settings["account_name"]
    requestCookies = {'POESESSID':stgs.settings["POESESSID"]}
    url = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + league + '&tabs=1&tabIndex=1&accountName=' + accountName
    endpoint = 'https://www.pathofexile.com/character-window/get-stash-items'

    while True:

        print(RL.checkRateLimit(endpoint))

        response = requests.get(url,cookies=requestCookies)

        RL.processResponse(endpoint, response.headers)

        input("Press enter to continue...")
    """

main()