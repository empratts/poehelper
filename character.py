"""
Character module allows for character tracking and planning.
-Monitors levels vs current zone to ensure you are not wasting time killing during leveling
-Tracks gems/sockets compared to a plan to give reminders to fix sockets/gems
-Tracks flasks compared to levels
-Tracks life/damage/resists and makes suggestions (trade links) on upgrades
-Tracks currency income vs what you plan to buy during leveling and recommends what to pick up/sell
-MODIFIES THE LOOT FILTER IN REAL TIME based on the above suggestions
"""
import json


class Character():
    def __init__(self, settings, inventory, api, log, itemFilter):
        self.settings = settings
        self.inventory = inventory
        self.api = api
        self.log = log
        self.itemFilter = itemFilter
        self.characterPlan = {}
        self.zonePlan = []
        self.level = 1
        self.currentZone = ""
        self.oldFilterString = ""
        self.oldZoneString = ""
        self.HUDUpdate = None

        self.loadCharacterPlan()
        self.loadZonePlan()

        self.log.registerCallback(self.logCallbackOnZoneChange, ": You have entered")
        self.log.registerCallback(self.logCallbackOnCharacterLevel, " \\(.*\\) is now level")
    
    def logCallbackOnZoneChange(self, text):
        self.inventory.updateCharacter()
        character = self.api.updateCharacter()
        if character != {}:
            self.level = character["level"]
        self.sendFilterUpdates()

        strIndex = text.find(": You have entered")
        self.currentZone = text[strIndex+19:-2]

        if self.HUDUpdate != None:
            self.HUDUpdate(self.getCharacterHUDString())
    
    def logCallbackOnCharacterLevel(self, text):
        parsedLevel = 0

        strIndex = text.find(") is now level ")
        parsedLevel = int(text[strIndex+15:-1])

        self.level = parsedLevel
        
        if self.HUDUpdate != None:
            self.HUDUpdate(self.getCharacterHUDString())
        
    def sendFilterUpdates(self):
        newString = self.getFlaskFilterString()
        if newString != self.oldFilterString:
            self.oldFilterString = newString
            self.itemFilter.addHighlight("Character - Flask", newString)

    def getFlaskFilterString(self):

        if self.characterPlan == {}:
            return ""

        #determine what flasks are equipped
        equippedFlasks = []

        for item in self.inventory.worn.values():
            if "Flask" in item["inventoryId"]:
                equippedFlasks.append(item["typeLine"])

        #determine what level of the flask progression the character is at
        recommendedSetup = {}
        for setup in self.characterPlan["Flasks"]:
            if setup["Level"] <= self.level:
                recommendedSetup = setup


        #for each life/mana flask in the current recommended setup, determine how far in the progression they are

        #Determine how many life flasks are recommended
        lifeCount = 0
        for flask in recommendedSetup["Bases"]:
            if "Life" in flask:
                lifeCount += 1

        #Make a list of the equipped life flasks
        lifeFlasks = []
        for flask in equippedFlasks:
            if "Life" in flask:
                lifeFlasks.append(flask)

        #for each flask progression, see how far the character is along it. The first porgressions get higher priority, and the flask that is furthest along
        #the earlier progression is not used for later progressions
        progress = []
        for i in range(lifeCount):
            progress.append(-1)
            progressFlask = ""
            for j in range(len(self.characterPlan["LifeProgression"][i])):
                for flask in lifeFlasks:
                    if self.characterPlan["LifeProgression"][i][j]["Size"] in flask and self.characterPlan["LifeProgression"][i][j]["Prefix"] in flask:
                        progress[-1] = j
                        progressFlask = flask
            
            if progressFlask in lifeFlasks:
                lifeFlasks.remove(progressFlask)

        #show/hide flasks based on their contribution to the progression
        
        #set the default highlight map to show nothing
        highlightMap = {"Small": {"Normal": False, "Magic": False},
                        "Medium": {"Normal": False, "Magic": False},
                        "Large": {"Normal": False, "Magic": False},
                        "Greater": {"Normal": False, "Magic": False},
                        "Grand": {"Normal": False, "Magic": False},
                        "Giant": {"Normal": False, "Magic": False},
                        "Colossal": {"Normal": False, "Magic": False},
                        "Sacred": {"Normal": False, "Magic": False},
                        "Hallowed": {"Normal": False, "Magic": False},
                        "Sanctified": {"Normal": False, "Magic": False},
                        "Divine": {"Normal": False, "Magic": False},
                        "Eternal": {"Normal": False, "Magic": False}}

        #turn on highlights for flasks that are past where the character is in their progressions
        for i in range(len(progress)):
            p = progress[i]
            progression = self.characterPlan["LifeProgression"][i]
            for j in range(p+1,len(progression)):
                size = progression[j]["Size"]
                prefix = progression[j]["Prefix"]
                if prefix == "":
                    highlightMap[size]["Normal"] = True
                highlightMap[size]["Magic"] = True

        #from the highlight map, produce the string
        baseString = "Show\n\tRarity {}\n\tBaseType {}\n\tSetBorderColor 0 0 0\n\tSetTextColor 0 0 0 255\n\tSetBackgroundColor 252 3 3 255\n\tSetFontSize 38\n\tPlayAlertSound 2 300\n\tPlayEffect White\n\tMinimapIcon 2 White Circle\n\n"

        normalBaseTypes = ""
        magicBaseTypes = ""

        for flask, highlight in highlightMap.items():
            if highlight["Normal"]:
                normalBaseTypes += "\"{} Life Flask\" ".format(flask)
            if highlight["Magic"]:
                magicBaseTypes += "\"{} Life Flask\" ".format(flask)

        finalString = ""
        if normalBaseTypes != "":
            finalString += baseString.format("Normal", normalBaseTypes)
        if magicBaseTypes != "":
            finalString += baseString.format("Magic", magicBaseTypes)

        return finalString

    def loadCharacterPlan(self):
        planFile = self.settings.getFileSettings("characterPlan")
        
        try:
            f = open(planFile, "r")
            self.characterPlan = json.load(f)
            f.close()
        except json.decoder.JSONDecodeError:
            print("Error loading JSON from character plan")

    def loadZonePlan(self):
        planFile = self.settings.getFileSettings("zonePlan")
        
        try:
            f = open(planFile, "r")
            self.zonePlan = json.load(f)
            f.close()
        except json.decoder.JSONDecodeError:
            print("Error loading JSON from character plan")

    def setHUDUpdate(self, updateFunction):
        self.HUDUpdate = updateFunction

    def getCharacterHUDString(self):
        HUDString = ""

        #Flask Info
        flaskString = ""
        for item in self.inventory.worn.values():
            if "Flask" in item["inventoryId"] and "Life" in item["typeLine"]:
                flaskString += "{} ".format(getFlaskRequiredLevel(item["typeLine"]))

        HUDString += "{},".format(flaskString)

        #Level/Exp info
        HUDString += "{}->{},".format(self.level, self.level + 3 + self.level//16)

        #Zone Info
        zoneLevelString = ""
        zoneNameString = ""
        for i in range(len(self.zonePlan)):
            if self.zonePlan[i]["Name"] == self.currentZone and self.level <= self.zonePlan[i]["Level"] + self.zonePlan[i]["MaxOverlevel"]:
                zonesToDisplay = min(5, len(self.zonePlan) - i)
                for j in range(zonesToDisplay):
                    if self.zonePlan[i+j]["Level"] < 10:
                        tempStr = "{}--"
                    else:
                        tempStr = "{}-"
                    zoneLevelString += tempStr.format(self.zonePlan[i+j]["Level"])
                    zoneNameString += "{}-".format(self.zonePlan[i+j]["Nickname"])
                
                self.oldZoneString = zoneLevelString[:-1] + "\n" + zoneNameString[:-1] + ","
                break


        HUDString += self.oldZoneString
        
        
        #Currency info
        HUDString += "Currency Info ,"

        return HUDString
    
def getFlaskRequiredLevel(typeLine):
    lifeFlaskLevels = {"Small": "1",
                    "Medium": "3",
                    "Large": "6",
                    "Greater": "12",
                    "Grand": "18",
                    "Giant": "24",
                    "Colossal": "30",
                    "Sacred": "36",
                    "Hallowed": "42",
                    "Sanctified": "50",
                    "Divine": "60",
                    "Eternal": "65"}

    if "Life" in typeLine:
        for flask in lifeFlaskLevels:
            if flask in typeLine:
                return lifeFlaskLevels[flask]