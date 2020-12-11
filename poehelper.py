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

    league = "Heist"
    accountName = "jumper315"#"jumper314""
    requestCookies = {'POESESSID':'56aedf579d1f6f05da01288f76886c46'}
    url = 'https://www.pathofexile.com/character-window/get-stash-items?league=' + league + '&tabs=1&tabIndex=1&accountName=' + accountName
    endpoint = 'https://www.pathofexile.com/character-window/get-stash-items'

    RL = RateLimiter()

    while True:
        response = requests.get(url,cookies=requestCookies)

        RL.processResponse(endpoint, response.headers)

        input("Press enter to continue...")

main()