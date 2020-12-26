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

    def modifySettings(self, newUnwrappedSettings):
        print(self.settings)
        for k, v in newUnwrappedSettings.items():
            self.updateSetting(k, v)
        print(self.settings)

        self.writeSettings()

    def updateSetting(self, wrapper, value):
        index = wrapper.split(":")

        setting = self.settings

        if len(index) > 1:
            for i in range(len(index)-1):
                setting = setting[index[i]]

        if type(setting[index[-1]]) == str:
            setting[index[-1]] = value
        else:
            setting[index[-1]] = json.loads(str(value))


    def listSettings(self):
        return unwrap(self.settings)

def unwrap(settings):
    result = {}
    for k, v in settings.items():
        if isinstance(v, dict):
            r = unwrap(v)
            for ele in r:
                result[k+":"+ele] = r[ele]
        else:
            result[k] = v
    return result

