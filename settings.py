"""
Settings module holds all current settings for the current instance of PoEHelper
    -Loads settings from file at startup
    -Tracks settings changes
    -Writes settings changes to file as needed.
"""

import json
from pathlib import Path

class Settings:

    def __init__(self):
        if Path('./settings.json').exists():
            #TODO: Add some more error checking here
            
            try:
                f = open("settings.json", "r")
                self.currentSettings = json.load(f)
                f.close()
            except json.decoder.JSONDecodeError:
                print("Error loading JSON from settings file, using defaults")
                #Dont enclose this in a try block. If this goes bad, we want a crash

                f = open("default_settings.json", "r")
                self.currentSettings = json.load(f)
                f.close()
                
                self.writeSettings()
                
        else:
            #same as above, crash here if default settings fail to load...change this later
            f = open("default_settings.json", "r")
            self.currentSettings = json.load(f)
            f.close()

            self.writeSettings()

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

    def updateFileSettings(self, fileName, path):
        #path should be a pathlib.Path object, not a string.
        fileName = "#!"+fileName

        self.currentSettings[fileName]["path"] = str(path.as_posix())

    def listSettings(self):
        return unwrap(self.currentSettings)
    
    def listWindows(self):
        #return a list of windows for which there are settings
        windows = []
        for setting in self.currentSettings:
            if setting[0] == "#" and setting[1] != "!":
                windows.append(setting[1:])
        return windows

    def listFiles(self):
        #return a list of files for which there are settings
        files = []
        for setting in self.currentSettings:
            if setting[:2] == "#!":
                files.append(setting[2:])
        return files

    def getWindowSettings(self, window):
        window = "#"+window
        if window in self.currentSettings:
            return self.currentSettings[window]
        else:
            return {"x":200,"y":200,"w":400,"h":600}

    def getFilePath(self, file):
        #returns a string pathname that should be fed to a pathlib.Path object
        file = "#!"+file
        if file in self.currentSettings:
            return self.currentSettings[file]["path"]
        else:
            return './'
    
    def getFileType(self, file):
        #returns a string extention of the file
        file = "#!"+file
        if file in self.currentSettings:
            return self.currentSettings[file]["type"]
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

