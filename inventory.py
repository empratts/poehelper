"""
Inventory module maintains a current picture of the players inventory, including worn gear
    -This module will parse the JSON responses from the API module to update the inventory on zone change
        -Parse the character on all zone changes
        -Parse the stash tabs on leaving a town zone (even if it is to enter another town zone)
            -This might get tricky once I start looking at zone names
    -This module will also monitor ctrl-clicking things in and out of the inventory while in towns (dumping and selling)
"""
#This dictionary is used to parse items. It contains all the properties to look for, and their default values should the property not exist in the API response
itemProperties = {"x":-5,"y":-5,"w":1,"h":1,"identified":True,"sockets":[],"typeLine":"","frameType":1,"ilvl":0,"inventoryId":"MainInventory","implicitMods":[],"explicitMods":[],"craftedMods":[],"socketedItems":[]}

class Inventory:

    def __init__(self, settings, api, logReader):
        self.settings = settings
        self.api = api
        self.logReader = logReader

        self.stash = {}
        self.stashFill = {}
        self.main = {}
        self.mainFill = []

        for x in range(12):
            self.mainFill.append([])
            for _ in range(5):
                self.mainFill[x].append("")

        self.worn = {}
        self.vendor = {}

        self.hideout = False

        self.logReader.registerCallback(self.logCallback, ": You have entered ")

    #this still needs to be updated. The inventory module should have other modules tell it when to update specific tabs.
    #Inventory should be generic and should not reference any other spcific module's settings
    def logCallback(self, logLines):
        if ": You have entered " in logLines and "Hideout." in logLines: #add more here for all towns. Also figure out what the game logs going in and out of the azurite mine
            if self.hideout:
                #moving from one safe zone to another, inspect both stash and character
                stash = self.api.updateStashTab("Chaos")
                tabIndex = self.settings.currentSettings["Chaos"]["index"]
                self.parseStash(stash, tabIndex)
                char = self.api.updateCharacter()
                self.parseCharacter(char)
            else:
                #moving from a non-stash zone to a safe zone, so only update the character
                char = self.api.updateCharacter()
                self.parseCharacter(char)

            self.enterHideout()

        elif ": You have entered " in logLines:
            if self.hideout:
                #Leaving a safe zone, inspect the stash and character
                stash = self.api.updateStashTab("Chaos")
                tabIndex = self.settings.currentSettings["Chaos"]["index"]
                self.parseStash(stash, tabIndex)
                char = self.api.updateCharacter()
                self.parseCharacter(char)
            else:
                #moving from a non-stash zone to another, only update the character
                char = self.api.updateCharacter()
                self.parseCharacter(char)

            for zone, level in self.settings.combatZones.items():
                if zone in logLines:
                    print(zone, level)

            self.leaveHideout()

    def parseStash(self, response, tabIndex):
        responseItems = response["items"]

        for description in response["tabs"]:
            if description["i"] == tabIndex:
                tabType = description["type"]

        if tabType == "QuadStash" or tabType == "PremiumStash" or tabType == "NormalStash":
            self.stashFill[tabIndex] = []
            if tabType == "QuadStash":
                for x in range(24):
                    self.stashFill[tabIndex].append([])
                    for _ in range(24):
                        self.stashFill[tabIndex][x].append("")
            else:
                for x in range(12):
                    self.stashFill[tabIndex].append([])
                    for _ in range(12):
                        self.stashFill[tabIndex][x].append("")

        self.purgeStash(tabIndex)

        for responseItem in responseItems:
            
            stashItem = parseItem(responseItem)
            self.stash[stashItem["id"]] = stashItem["properties"]

            if tabIndex in self.stashFill:
                x = stashItem["properties"]["x"]
                y = stashItem["properties"]["y"]
                w = stashItem["properties"]["w"]
                h = stashItem["properties"]["h"]
                for w in range(stashItem["properties"]["w"]):
                    for h in range(stashItem["properties"]["h"]):
                        self.stashFill[tabIndex][x+w][y+h] = stashItem["id"]

        return

    def purgeStash(self, tabIndex):
        inventoryId = "Stash" + str(tabIndex + 1)

        staleItems = []

        for item in self.stash:
            if self.stash[item]["inventoryId"] == inventoryId:
                staleItems.append(item)

        for item in staleItems:
            self.stash.pop(item)

    def parseCharacter(self, response):
        responseItems = response["items"]
        self.worn = {}
        self.main = {}

        for x in range(12):
            for y in range(5):
                self.mainFill[x][y] = ""

        for responseItem in responseItems:
            if responseItem["inventoryId"] == "MainInventory":
                mainItem = parseItem(responseItem)
                
                self.main[mainItem["id"]] = mainItem["properties"]

                x = mainItem["properties"]["x"]
                y = mainItem["properties"]["y"]

                for w in range(mainItem["properties"]["w"]):
                    for h in range(mainItem["properties"]["h"]):
                        self.mainFill[x+w][y+h] = mainItem["id"]

            else:
                wornItem = parseItem(responseItem)
                
                self.worn[wornItem["id"]] = wornItem["properties"]
        
        return

    def clickToStash(self, tab, x, y):
        #Takes an X and Y inventory spot from the main inventory and ctrl clicks that item into the stash

        #TODO:add functionality to manage affinity items

        #look up the item to get dimensions
        if not tab in self.stashFill:
            return
        ID = self.mainFill[x][y]
        w = self.main[ID]["w"]
        h = self.main[ID]["h"]
        x = self.main[ID]["x"]
        y = self.main[ID]["y"]

        #see if it will fit in the tab
        fits = False
        for i in range(len(self.stashFill[tab])):
            for j in range(len(self.stashFill[tab][i])):
                fits = True
                for k in range(w):
                    for l in range(h):
                        if self.stashFill[tab][i+k][j+l] != "":
                            fits = False
                if fits:
                    #if so, remove it from the main inventory and place it in the stash
                    for k in range(w):
                        for l in range(h):
                            self.stashFill[tab][i+k][j+l] = ID
                            self.mainFill[x+k][y+l] = ""

                    item = self.main[ID]
                    item["x"] = i
                    item["y"] = j
                    item["inventoryId"] = "Stash" + str(tab + 1)
                    self.stash[ID] = item 
                    self.main.pop(ID)
                    break
            if fits:
                break
        return

    def clickFromStash(self, tab, x, y):
        #takes an X and Y inventory position and a tab index and moves that item to the main inventory.
        
        #look up the item to get dimensions
        if not tab in self.stashFill:
            return
        
        ID = self.stashFill[tab][x][y]
        w = self.stash[ID]["w"]
        h = self.stash[ID]["h"]
        x = self.stash[ID]["x"]
        y = self.stash[ID]["y"]

        #see if it will fit in the tab
        fits = False
        item = None
        for i in range(len(self.mainFill)-w):
            for j in range(len(self.mainFill[i])-h):
                fits = True
                for k in range(w):
                    for l in range(h):
                        if self.mainFill[i+k][j+l] != "":
                            fits = False
                if fits:
                    #if so, remove it from the stash and place it in the main inventory
                    for k in range(w):
                        for l in range(h):
                            self.mainFill[i+k][j+l] = ID
                            self.stashFill[tab][x+k][y+l] = ""

                    item = self.stash[ID]
                    item["x"] = i
                    item["y"] = j
                    item["inventoryId"] = "MainInventory"
                    self.main[ID] = item 
                    self.stash.pop(ID)
                    break
            if fits:
                print("Item moved to main Inventory" + str(item))
                break
        return

    def clickToVendor(self, x, y):
        #takes and X and Y inventory spot and ctrl clicks those items into the vendor window
        return
    
    def clickfromVendor(self, x, y):
        #takes and X and Y inventory spot and ctrl clicks those items out of the vendor window
        return

    def confirmVendor(self):
        #confirms sale of the items in the vendor window
        return

    def enterHideout(self):
        self.hideout = True
    
    def leaveHideout(self):
        self.hideout = False

def parseItem(responseItem):
    item = {}
    for prop in itemProperties:
        if prop in responseItem:
            item[prop] = responseItem[prop]
        else:
            item[prop] = itemProperties[prop]
    
    return {"id":responseItem["id"], "properties":item}