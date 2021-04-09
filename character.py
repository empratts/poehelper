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
import re
from pathlib import Path

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
        self.classId = -1
        self.allocatedPassives = {}
        self.passiveTreeStats = {}
        self.currentZone = ""
        self.oldFilterString = ""
        self.oldZoneString = ""
        self.HUDUpdate = None
        self.charDefStats = {"Life": 0,"Fire": 0,"Cold": 0,"Lightning": 0,"Chaos": 0, "Strength":0, "Dexterity":0, "Intelligence":0}
        self.equippedItemStats = {}
        self.characterUpdatedCallback = None

        self.loadCharacterPlan()
        self.loadZonePlan()

        self.basePassiveTree = {}
        if Path('./passiveTree/data.json').exists():
            try:
                f = open('./passiveTree/data.json', 'r')
                self.basePassiveTree = json.load(f)
                f.close()
            except json.decoder.JSONDecodeError:
                print("Error loading JSON from passive tree data file")
        else:
            print("Passive tree data unavailable")

        self.log.registerCallback(self.logCallbackOnZoneChange, ": You have entered")
        self.log.registerCallback(self.logCallbackOnCharacterLevel, " \\(.*\\) is now level")
    
    def logCallbackOnZoneChange(self, text):
        self.inventory.updateCharacter()
        character = self.api.updateCharacter()
        if character != {}:
            self.level = character["level"]
            self.classId = character["classId"]
        self.sendFilterUpdates()

        self.allocatedPassives = self.api.updateCharacterPassiveTree()
        self.updateStatsFromPassives()

        strIndex = text.find(": You have entered")
        self.currentZone = text[strIndex+19:-2]

        changed = self.parseInventoryForDefenses()

        if self.HUDUpdate != None:
            self.HUDUpdate(self.getCharacterHUDString())
        
        if self.characterUpdatedCallback != None and changed:
            self.characterUpdatedCallback()
    
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
        planFile = self.settings.getFilePath("characterPlan")
        
        try:
            f = open(planFile, "r")
            self.characterPlan = json.load(f)
            f.close()
        except json.decoder.JSONDecodeError:
            print("Error loading JSON from character plan")

    def loadZonePlan(self):
        planFile = self.settings.getFilePath("zonePlan")
        
        try:
            f = open(planFile, "r")
            self.zonePlan = json.load(f)
            f.close()
        except json.decoder.JSONDecodeError:
            print("Error loading JSON from character plan")

    def setHUDUpdate(self, callback):
        #call this function after things have changed to update the HUD
        #TODO: Look at combining this with regesterUIUpdate and possibly generalize how modules send updates to the UI so that the UI code dose not reference specific modules.
        self.HUDUpdate = callback

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
    
    def parseInventoryForDefenses(self):
        changed = False

        self.charDefStats = {"Life": 0,"Fire": 0,"Cold": 0,"Lightning": 0,"Chaos": 0, "Strength":0, "Dexterity":0, "Intelligence":0}
        
        equippedItems = []

        for item in self.inventory.worn.values():
            if not("Flask" in item["inventoryId"] or "MainInventory" in item["inventoryId"] or "Weapon2" in item["inventoryId"] or "Offhand2" in item["inventoryId"]):
                equippedItems.append(item)

        for item in equippedItems:
            itemStats = getParsedItemDefenses(item)
            for stat in self.charDefStats:
                self.charDefStats[stat] += itemStats[stat]

            if item["inventoryId"] in self.equippedItemStats:
                oldItem = self.equippedItemStats[item["inventoryId"]]
                for stat in oldItem:
                    if "Score" not in stat and oldItem[stat] != itemStats[stat]:
                        self.equippedItemStats[item["inventoryId"]] = itemStats
                        changed = True
                        break
            else:
                self.equippedItemStats[item["inventoryId"]] = itemStats
                changed = True
        
        if changed:
            #at this point, the charDefStats dict only contains stats from items. This is currently assumed before calculating gear scores
            self.generateGearDefScores()

        #this may not be the right place to combine the passive tree data and char def stats,
        #but until a more complete method of generating gear scores is implemented, this is the simplest place
        self.charDefStats["Strength"] += self.passiveTreeStats["grantedStrength"]
        self.charDefStats["Dexterity"] += self.passiveTreeStats["grantedDexterity"]
        self.charDefStats["Intelligence"] += self.passiveTreeStats["grantedIntelligence"]

        print(self.charDefStats)
        return changed
    
    def generateGearDefScores(self):
        for invId, item in self.equippedItemStats.items():
            fireScore = 0
            coldScore = 0
            lightningScore = 0
            chaosScore = 0
            lifeScore = 0

            if self.charDefStats["Fire"] > 0:
                fireScore = 100.0 * ( 1.0 - min(135, self.charDefStats["Fire"] - item["Fire"])/min(135, self.charDefStats["Fire"]))
            
            if self.charDefStats["Cold"] > 0:
                coldScore = 100.0 * ( 1.0 - min(135, self.charDefStats["Cold"] - item["Cold"])/min(135, self.charDefStats["Cold"]))
            
            if self.charDefStats["Lightning"] > 0:
                lightningScore = 100.0 * ( 1.0 - min(135, self.charDefStats["Lightning"] - item["Lightning"])/min(135, self.charDefStats["Lightning"]))
            
            if self.charDefStats["Chaos"] > 0:
                chaosScore = 100.0 * ( 1.0 - min(135, self.charDefStats["Chaos"] - item["Chaos"])/min(135, self.charDefStats["Chaos"]))
            
            if self.charDefStats["Life"] > 0:
                lifeScore = 100* (1- (self.charDefStats["Life"] - item["Life"])/self.charDefStats["Life"])

            resScore = (fireScore + coldScore + lightningScore + chaosScore) / 4.0

            self.equippedItemStats[invId]["ResScore"] = resScore
            self.equippedItemStats[invId]["LifeScore"] = lifeScore

            #print("{} -> {}".format(invId,self.equippedItemStats[invId]))

    def registerUIUpdate(self, callback):
        #call this function after the character inventory is updated to let the UI know that things have changed
        self.characterUpdatedCallback = callback

    def updateStatsFromPassives(self):
        #start counting stats from the base values that each class gets
        baseClass = self.basePassiveTree['classes'][self.classId]
        self.passiveTreeStats = { "grantedStrength": baseClass["base_str"], "grantedDexterity": baseClass["base_dex"], "grantedIntelligence": baseClass["base_int"]}
        
        #iterate throught all allocated nodes and look them up in the base passive tree to get their stats
        for allocatedNode in self.allocatedPassives["hashes"]:
            nodeString = str(allocatedNode)
            node = self.basePassiveTree["nodes"][nodeString]
            
            for stat in self.passiveTreeStats:
                if stat in node:
                    self.passiveTreeStats[stat] += node[stat]

    def getEffectiveFireResist(self,item):
        stats = self.equippedItemStats[item]

        fire = self.charDefStats["Fire"] - stats["Fire"]
        
        total = 0

        if fire < 135:
            total += min(135, self.charDefStats["Fire"]) - fire

        return total

    def getEffectiveColdResist(self,item):
        stats = self.equippedItemStats[item]

        cold = self.charDefStats["Cold"] - stats["Cold"]
        
        total = 0

        if cold < 135:
            total += min(135, self.charDefStats["Cold"]) - cold

        return total

    def getEffectiveLightningResist(self,item):
        stats = self.equippedItemStats[item]

        lightning = self.charDefStats["Lightning"] - stats["Lightning"]
        
        total = 0

        if lightning < 135:
            total += min(135, self.charDefStats["Lightning"]) - lightning

        return total

    def getEffectiveEleResist(self,item):
        stats = self.equippedItemStats[item]

        fire = self.charDefStats["Fire"] - stats["Fire"]
        cold = self.charDefStats["Cold"] - stats["Cold"]
        lightning = self.charDefStats["Lightning"] - stats["Lightning"]

        total = 0

        if fire < 135:
            total += min(135, self.charDefStats["Fire"]) - fire
        if cold < 135:
            total += min(135, self.charDefStats["Cold"]) - cold
        if lightning < 135:
            total += min(135, self.charDefStats["Lightning"]) - lightning

        return total

    def getEffectiveResist(self,item):
        stats = self.equippedItemStats[item]

        fire = self.charDefStats["Fire"] - stats["Fire"]
        cold = self.charDefStats["Cold"] - stats["Cold"]
        lightning = self.charDefStats["Lightning"] - stats["Lightning"]
        chaos = self.charDefStats["Chaos"] - stats["Chaos"]

        total = 0

        if fire < 135:
            total += min(135, self.charDefStats["Fire"]) - fire
        if cold < 135:
            total += min(135, self.charDefStats["Cold"]) - cold
        if lightning < 135:
            total += min(135, self.charDefStats["Lightning"]) - lightning
        if chaos < 135:
            total += min(135, self.charDefStats["Chaos"]) - chaos

        return total

def getParsedItemDefenses(item):
    resRegex = r'\+(\d*)% to (.*) Resistance'
    lifeRegex = r'\+(\d*) to maximum Life|\+(\d*) to (?:Strength|All Attributes)'
    statRegex = r'\+(\d*) to (?:Strength|Dexterity|Intelligence|All Attributes)'
    resCheck = re.compile(resRegex)
    lifeCheck = re.compile(lifeRegex)
    statCheck = re.compile(statRegex)

    itemStats = {"Life": 0,"Fire": 0,"Cold": 0,"Lightning": 0,"Chaos": 0, "All Elemental": 0, "Strength":0, "Dexterity":0, "Intelligence":0, "LifeScore": 0.0, "ResScore": 0.0 }

    if "implicitMods" in item:
        for mod in item["implicitMods"]:
            m = resCheck.match(mod)
            if m != None:
                roll = int(m.group(1))
                for stat in itemStats:
                    if stat in m.group(2):
                        itemStats[stat] += roll
            
            m = lifeCheck.match(mod)
            if m != None:
                if m.group(1) != None:
                    roll = int(m.group(1))
                else:
                    roll = 0.5 * int(m.group(2))

                itemStats["Life"] += roll

            m = statCheck.match(mod)
            if m != None:
                stats = ["Strength", "Dexterity", "Intelligence"]
                for stat in stats:
                    if stat in mod or "All Attributes" in mod:
                        itemStats[stat] += int(m.group(1))

    
    if "explicitMods" in item:
        for mod in item["explicitMods"]:
            m = resCheck.match(mod)
            if m != None:
                roll = int(m.group(1))
                for stat in itemStats:
                    if stat in m.group(2):
                        itemStats[stat] += roll

            m = lifeCheck.match(mod)
            if m != None:
                if m.group(1) != None:
                    roll = int(m.group(1))
                else:
                    roll = 0.5 * int(m.group(2))
                    
                itemStats["Life"] += roll
            
            m = statCheck.match(mod)
            if m != None:
                stats = ["Strength", "Dexterity", "Intelligence"]
                for stat in stats:
                    if stat in mod or "All Attributes" in mod:
                        itemStats[stat] += int(m.group(1))
    
    itemStats["Fire"] += itemStats["All Elemental"]
    itemStats["Cold"] += itemStats["All Elemental"]
    itemStats["Lightning"] += itemStats["All Elemental"]
    itemStats.pop("All Elemental")

    return itemStats

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