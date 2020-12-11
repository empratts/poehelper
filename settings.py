"""
Settings module holds all current settings for the current instance of PoEHelper
    -Loads settings from file at startup
    -Tracks settings changes
    -Writes settings changes to file as needed.
"""

import json
from pathlib import Path
import requests

class Settings:
    #default settings in the event that settings.json is empty
    defaultSettings = {'league':'',
                       'account_name':'',
                       'character_name':'',
                       'POESESSID': '',
                       'resolution': {'x':2560, 'y':1440},
                       'chaos':{"item_limit":{'body':6,'weapon':12,'glove':6,'boot':6,'helm':6,'belt':30,'amulet':128,'ring':256},'preserve_low_level':False,'disable_recipe':False, 'tabs':{'n':'C','quad':True}}}
                       #TODO Add more settings as needed:
                       #stash settings, inc dump tabs, chaos tabs etc.
                       #Inventory, button, and window locations
                       #character planner settings

    def __init__(self):
        if Path('./settings.json').exists():
            #TODO: Add some more error checking here
            
            try:
                f = open("settings.json", "r")
                self.settings = json.load(f)
                f.close()
            except json.decoder.JSONDecodeError:
                print("Error loading JSON from settings file, using defaults")
                self.settings = self.defaultSettings
                self.writeSettings()
                #TODO: add some way of recovering broken settings file instead of just overwriting it?
            
        else:
            self.settings = self.defaultSettings
            self.writeSettings()

        resetString = input("Would you like to reset charater settings? YES / NO: ")
        reset = False
        if("yes" == resetString.lower()):
            reset = True
        if ('' == self.settings["league"] or '' == self.settings["account_name"] or '' == self.settings["character_name"] or '' == self.settings["POESESSID"] or reset):
            #TODO pop up setting dialog
            self.promptSettings(reset)
            self.writeSettings()



    def writeSettings(self):
        #TODO: Add some error checking here
        f = open("settings.json", "w")
        json.dump(self.settings, f)
        f.close()

    def promptSettings(self, reset):
        if('' == self.settings["account_name"] or reset): #TODO or invalid
            self.settings["account_name"] = input("Enter account name:")
        if('' == self.settings["POESESSID"] or reset): #TODO or invalid
            self.settings["POESESSID"] = input("Enter POESESSID:")
        if('' == self.settings["league"] or reset):          
            url = 'http://api.pathofexile.com/leagues?type=main&compact=1'
            response = requests.get(url,cookies='')
            leagueList = list(eval(response.text.replace("null", "None").replace("true", "True").replace("false", "False")))
            for item in leagueList:
                print(item["id"])
            self.settings["league"] = input("Enter league:")
        if('' == self.settings["character_name"] or reset):          
            url = 'https://www.pathofexile.com/character-window/get-characters?&accountName=' + self.settings["account_name"]
            response = requests.get(url,cookies='')
            characterList = list(eval(response.text))
            for character in characterList:
                if(self.settings["league"] == character["league"]):
                    print(character["name"])
            self.settings["character_name"] = input("Enter character:")

    def modifySettings(self, newSettings):
        self.settings = newSettings
        self.writeSettings()

    def listSettings(self):
        return self.settings.keys()
