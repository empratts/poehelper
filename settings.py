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
                self.currentSettings = json.load(f)
                f.close()
            except json.decoder.JSONDecodeError:
                print("Error loading JSON from settings file, using defaults")
                self.currentSettings = self.defaultSettings
                self.writeSettings()
                #TODO: add some way of recovering broken settings file instead of just overwriting it?
            
        else:
            self.currentSettings = self.defaultSettings
            self.writeSettings()

        self.combatZones = {}

        #load zone names and levels
        if Path('./combatZones.txt').exists():
            f = open('combatZones.txt', "r")
            content = f.readlines()
            f.close()

            for line in content:
                zone = line.strip("\n").split("-")
                if zone[0] in self.combatZones:
                    self.combatZones[zone[0]].append(int(zone[1]))
                else:
                    self.combatZones[zone[0]] = [int(zone[1])]
        
        self.townZones = []

        #load zone names and levels
        if Path('./townZones.txt').exists():
            f = open('townZones.txt', "r")
            content = f.readlines()
            f.close()

            for line in content:
                zone = line.strip("\n")
                self.townZones.append(zone)

    def writeSettings(self):
        #TODO: Add some error checking here
        f = open("settings.json", "w")
        json.dump(self.currentSettings, f, indent=4)
        f.close()

    def modifySettings(self, newWrappedSettings):
        for k, v in newWrappedSettings.items():
            self.updateWrappedSetting(k, v)

        self.writeSettings()

    def updateWrappedSetting(self, wrapper, value):
        index = wrapper.split(":")

        setting = self.currentSettings

        if len(index) > 1:
            for i in range(len(index)-1):
                setting = setting[index[i]]

        if type(setting[index[-1]]) == str:
            setting[index[-1]] = value
        else:
            setting[index[-1]] = json.loads(str(value))

    def updateWindowSettings(self, window, w, h, x, y):
        window = "#"+window

        if not window in self.currentSettings:
            self.currentSettings[window] = {}
        
        self.currentSettings[window]["x"] = x
        self.currentSettings[window]["y"] = y
        self.currentSettings[window]["w"] = w
        self.currentSettings[window]["h"] = h

        self.writeSettings()

    def updateFileSettings(self, file, path):
        #path should be a pathlib.Path object, not a string.
        file = "#!"+file

        self.currentSettings[file] = str(path.as_posix())

    def listSettings(self):
        return unwrap(self.currentSettings)
    
    def getWindowSettings(self, window):
        window = "#"+window
        if window in self.currentSettings:
            return self.currentSettings[window]
        else:
            return {"x":200,"y":200,"w":400,"h":600}

    def getFileSettings(self, file):
        #returns a string pathname that should be fed to a pathlib.Path object
        file = "#!"+file
        if file in self.currentSettings:
            return self.currentSettings[file]
        else:
            return '.'

def unwrap(settings):
    result = {}
    for k, v in settings.items():
        if k[0] != "#":
            if isinstance(v, dict):
                r = unwrap(v)
                for ele in r:
                    result[k+":"+ele] = r[ele]
            else:
                result[k] = v
    return result

