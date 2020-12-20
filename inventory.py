"""
Inventory module maintains a current picture of the players inventory, including worn gear
    -This module will parse the JSON responses from the API module to update the inventory on zone change
        -Parse the character on all zone changes
        -Parse the stash tabs on leaving a town zone (even if it is to enter another town zone)
            -This might get tricky once I start looking at zone names
    -This module will also monitor ctrl-clicking things in and out of the inventory while in towns (dumping and selling)
"""

class Inventory:

    def __intit__(self):
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

    def parseStash(self, response, tab):
        items = response["items"]

        for description in response["tabs"]:
            if description["i"] == tab:
                tabType = description["type"]

        if tabType == "QuadStash" or tabType == "PremiumStash" or tabType == "NormalStash":
            self.stashFill[tab] = []
            if tabType == "QuadStash":
                for x in range(24):
                    self.stashFill[tab].append([])
                    for _ in range(24):
                        self.stashFill[tab][x].append("")
            else:
                for x in range(12):
                    self.stashFill[tab].append([])
                    for _ in range(12):
                        self.stashFill[tab][x].append("")

        for item in items:
            if item["id"] in self.stash:
                itemInfo = self.stash[item["id"]]
                itemInfo["x"] = item["x"]
                itemInfo["y"] = item["y"]
                itemInfo["tab"] = tab
                #this part might need to include deleting and completely redoing the item in the database if it is common for items to get modified after being added
            else:
                stashItem = {"x":item["x"],"y":item["y"],"w":item["w"],"h":item["h"],"tab":tab}
                
                if "ilvl" in item:
                    stashItem["ilvl"] = item["ilvl"]
                else:
                    stashItem["ilvl"] = 0
                if "identified" in item:
                    stashItem["identified"] = item["identified"]
                else:
                    stashItem["identified"] = True
                if "sockets" in item:
                    stashItem["sockets"] = item["sockets"]
                else:
                    stashItem["sockets"] = []
                if "typeLine" in item: #Item typeLine is the items base type
                    stashItem["baseType"] = item["typeLine"]
                else:
                    stashItem["baseType"] = ""
                if "frameType" in item:#frameTyep includes rarity info, and other classification info. See Wiki
                    stashItem["frameType"] = item["frameType"]
                else:
                    stashItem["frameType"] = -1
                    #porbably add other attributes as they become needed by other modules
                self.stash[item["id"]] = stashItem

            if tab in self.stashFill:
                x = item["x"]
                y = item["y"]
                w = item["w"]
                h = item["h"]
                for w in range(item["w"]):
                    for h in range(item["h"]):
                        self.stashFill[tab][x+w][y+h] = item["id"]

        return

    def parseCharacter(self, response):
        items = response["items"]
        self.worn = {}
        self.main = {}

        for x in range(12):
            for y in range(5):
                self.mainFill[x][y] = ""

        for item in items:
            if item["inventoryID"] == "MainInventory":
                mainItem = {"x":item["x"],"y":item["y"],"w":item["w"],"h":item["h"],"tab":"MainInventory"}
                
                if "ilvl" in item:
                    mainItem["ilvl"] = item["ilvl"]
                else:
                    mainItem["ilvl"] = 0
                if "identified" in item:
                    mainItem["identified"] = item["identified"]
                else:
                    mainItem["identified"] = True
                if "sockets" in item:
                    mainItem["sockets"] = item["sockets"]
                else:
                    mainItem["sockets"] = []
                if "typeLine" in item: #Item typeLine is the items base type
                    mainItem["baseType"] = item["typeLine"]
                else:
                    mainItem["baseType"] = ""
                if "frameType" in item:#frameType includes rarity info, and other classification info. See Wiki
                    mainItem["frameType"] = item["frameType"]
                else:
                    mainItem["frameType"] = -1
                    #porbably add other attributes as they become needed by other modules
                self.main[item["id"]] = mainItem

                x = item["x"]
                y = item["y"]

                for w in range(item["w"]):
                    for h in range(item["h"]):
                        self.mainFill[x+w][y+h] = item["id"]

            else:
                wornItem = {"slot":item["inventoryID"], "baseType":item["typeLine"], "ilvl":item["ilvl"]}
                if "implicitMods" in item:
                    wornItem["implicitMods"] = item["implicitMods"]
                else:
                    wornItem["implicitMods"] = []
                if "explicitMods" in item:
                    wornItem["explicitMods"] = item["explicitMods"]
                else:
                    wornItem["explicitMods"] = []
                if "craftedMods" in item:
                    wornItem["craftedMods"] = item["craftedMods"]
                else:
                    wornItem["craftedMods"] = []
                if "sockets" in item:
                    wornItem["sockets"] = item["sockets"]
                else:
                    wornItem["sockets"] = []
                if "socketedItems" in item:
                    wornItem["socketedItems"] = item["socketedItems"]
                else:
                    wornItem["socketedItems"] = [] #any further tracking that needs to happen for sockets or affixes should be managed by the other modules unless there is some data that needs to be saved that we are missing
                
                self.worn[item["id"]] = wornItem
                
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
                    self.stash[ID] = item
                    self.main.pop(ID)
                    break
            if fits:
                break
        return

    def clickFromStash(self, tab, x, y):
        #takes and X and Y inventory position and a tab index and moves that item to the main inventory.
        if not 
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

    