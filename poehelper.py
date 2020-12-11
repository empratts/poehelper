#Main driver for PoEHelper
from settings import Settings
from api import RateLimiter
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

main()