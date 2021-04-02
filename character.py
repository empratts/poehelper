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
    def __init__(self, settings, inventory, log, itemFilter):
        self.settings = settings
        self.inventory = inventory
        self.log = log
        self.itemFilter = itemFilter
        self.plan = {}
        self.level = 1
        self.oldFilterString = ""

        self.loadCharacterPlan()

        self.log.registerCallback(self.logCallback, ": You have entered")
    
    def logCallback(self, text):
        self.inventory.updateCharacter()
        self.sendFilterUpdates()

    def sendFilterUpdates(self):
        newString = self.getFlaskFilterString()
        if newString != self.oldFilterString:
            self.oldFilterString = newString
            self.itemFilter.addHighlight("Character - Flask", newString)

    def getFlaskFilterString(self):

        if self.plan == {}:
            return ""

        #determine what flasks are equipped
        equippedFlasks = []

        for item in self.inventory.worn.values():
            if "Flask" in item["inventoryId"]:
                equippedFlasks.append(item["typeLine"])

        #determine what level of the flask progression the character is at
        recommendedSetup = {}
        for setup in self.plan["Flasks"]:
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
            for j in range(len(self.plan["LifeProgression"][i])):
                for flask in lifeFlasks:
                    if self.plan["LifeProgression"][i][j]["Size"] in flask and self.plan["LifeProgression"][i][j]["Prefix"] in flask:
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
            progression = self.plan["LifeProgression"][i]
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
            self.plan = json.load(f)
            f.close()
        except json.decoder.JSONDecodeError:
            print("Error loading JSON from character plan")
