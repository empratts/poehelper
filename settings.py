"""
Settings module holds all current settings for the current instance of PoEHelper
    -Loads settings from file at startup
    -Tracks settings changes
    -Writes settings changes to file as needed.
"""

import json
from pathlib import Path

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

    def writeSettings(self):
        #TODO: Add some error checking here
        f = open("settings.json", "w")
        json.dump(self.settings, f)
        f.close()

    def modifySettings(self, newSettings):
        self.settings = newSettings
        self.writeSettings()

    def listSettings(self):
        return self.settings.keys()
