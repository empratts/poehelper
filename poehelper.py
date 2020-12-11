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

    settings = Settings()

    league = settings.settings["league"]
    accountName = settings.settings["account_name"]
    requestCookies = {'POESESSID':settings.settings["POESESSID"]}
    url = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + league + '&tabs=1&tabIndex=1&accountName=' + accountName
    endpoint = 'https://www.pathofexile.com/character-window/get-stash-items'

    RL = RateLimiter()

    while True:

        print(RL.checkRateLimit(endpoint))

        response = requests.get(url,cookies=requestCookies)

        RL.processResponse(endpoint, response.headers)

        input("Press enter to continue...")

main()