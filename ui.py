from tkinter import Tk, Canvas, Frame, Toplevel, Label, Entry, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED, DISABLED, filedialog
from functools import partial
import time
import json
import threading
import time
from datetime import datetime
import win32api, win32gui, win32con
from pathlib import Path
import webbrowser
#from log import ReadLogFile

class UserInterface(Frame):

    def __init__(self, master, settings, inventory, api, chaos, log, character):
        super().__init__(master=master)

        self.initUI(settings, inventory, api, chaos, log, character)

    def initUI(self, settings, inventory, api, chaos, log, character):

        self.master.title("PoE Helper")
        self.pack(fill=BOTH, expand=1)
        self.menu = None
        self.control = None
        self.chaosOverlay = None
        self.mainOverlay = None
        self.vendorOverlay = None
        self.settings = settings
        self.inventory = inventory
        self.api = api
        self.chaos = chaos
        self.log = log
        self.character = character
        self.hideout = False

        self.canvas = Canvas(self, bd=-2)
        self.canvas.config(bg='white')
        self.canvas.pack(fill=BOTH, expand=1)

        self.menuButton = Button(self.canvas, text="Menu", command=self.optionsMenu, anchor=N)
        self.menuButton.place(x=self.winfo_screenwidth()/2 + 30, y=0)

        self.controlButton = Button(self.canvas, text="Control", command=self.controlPannel, anchor=N)
        self.controlButton.place(x=self.winfo_screenwidth()/2 + 90, y=0)

        self.chaosButton = Button(self.canvas, text="Chaos", command=self.toggleChaosOverlay, anchor=N)
        self.chaosButton.place(x=self.winfo_screenwidth()/2 - 30, y=0)

        #self.updateButton = Button(self.canvas, text="update", command=self.updateStash, anchor=N)
        #self.updateButton.place(x=self.winfo_screenwidth()/2 - 30, y=25)

        self.chaosHUD = None
        self.initChaosHUD()

        self.characterHUD = None
        self.initCharacterHUD()

        self.redraw()

    def redraw(self):
        return

    def optionsMenu(self):
        if self.menu is None:
            self.menu = SettingsMenu(self.master, self)
        else:
            self.closeOptionsMenu()
    
    def closeOptionsMenu(self):
        self.settings.updateWindowSettings("Menu", self.menu.winfo_width(), self.menu.winfo_height(), self.menu.winfo_x(), self.menu.winfo_y())
        self.menu.destroy()
        self.menu = None

    def controlPannel(self):
        if self.control is None:
            self.control = ControlPannel(self.master, self)
        else:
            self.closeControlPannel()

    def closeControlPannel(self):
        self.settings.updateWindowSettings("Control", self.control.winfo_width(), self.control.winfo_height(), self.control.winfo_x(), self.control.winfo_y())
        self.control.destroy()
        self.control = None

    def initChaosHUD(self):
        settings = self.settings.getWindowSettings("ChaosHUD")
        self.chaosHUD = HUDOverlay(self,settings["x"],settings["y"],settings["w"],settings["h"],8, settings["colors"])
        self.chaos.setHUDUpdate(self.chaosHUD.updateText)

    def initCharacterHUD(self):
        settings = self.settings.getWindowSettings("CharacterHUD")
        self.characterHUD = HUDOverlay(self,settings["x"],settings["y"],settings["w"],settings["h"],4, settings["colors"])
        self.character.setHUDUpdate(self.characterHUD.updateText)

    def toggleChaosOverlay(self):

        if self.chaosOverlay is None:
            settings = self.settings.getWindowSettings("Chaos")
            self.chaosOverlay = InventoryOverlay(self,settings["x"],settings["y"],settings["w"],settings["h"],settings["cellGap"],settings["border"],settings["tabType"])
            
            chaosSet = self.chaos.getChaosSet()

            for item in chaosSet:
                x = self.inventory.stash[item]["x"]
                y = self.inventory.stash[item]["y"]
                w = self.inventory.stash[item]["w"]
                h = self.inventory.stash[item]["h"]
                self.chaosOverlay.addHighlight(x,y,w,h,"#90fc03")

        else:
            self.chaosOverlay.destroy()
            self.chaosOverlay = None

        """#Possibly leave out or remove this functionality... Not 100% sure it is worth the time to finish. At this point I think other functions will be more worthwhile
        if self.mainOverlay is None:
            settings = self.settings.getWindowSettings("Main")
            self.mainOverlay = Overlay(self,settings["x"],settings["y"],settings["w"],settings["h"],settings["cellGap"],settings["border"],settings["tabType"])
            for i in range(5):
                self.mainOverlay.addHighlight(i,i,1,1,"#90fc03")
        else:
            self.mainOverlay.destroy()
            self.mainOverlay = None

        if self.vendorOverlay is None:
            settings = self.settings.getWindowSettings("Vendor")
            self.vendorOverlay = Overlay(self,settings["x"],settings["y"],settings["w"],settings["h"],settings["cellGap"],settings["border"],settings["tabType"])
            for i in range(5):
                self.vendorOverlay.addHighlight(i,i,1,1,"#90fc03")
        else:
            self.vendorOverlay.destroy()
            self.vendorOverlay = None
        """

    def closeChaosOverlay(self):
        self.chaosOverlay.destroy()
        self.chaosOverlay = None

    def killAllThreads(self):
        if self.menu is not None:
            self.menu.destroy()
        if self.chaosOverlay is not None:
            self.chaosOverlay.destroy()
        if self.mainOverlay is not None:
            self.mainOverlay.destroy()
        if self.vendorOverlay is not None:
            self.vendorOverlay.destroy()

    def enterHideout(self):
        self.hideout = True
        #add code here to show/hide the stuff that you want to see while in the HO
    
    def leaveHideout(self):
        self.hideout = False
        #add code here to show/hide the stuff that you want to see while actually playing

class SettingsMenu(Toplevel):

    def __init__(self, master=None, parent=None):
        super().__init__(master=master)

        self.initMenu(parent)

    def initMenu(self, parent):

        self.parent = parent

        self.title("Menu")

        windowSettings = parent.settings.getWindowSettings("Menu")
        self.geometry("{}x{}+{}+{}".format(windowSettings["w"], windowSettings["h"], windowSettings["x"], windowSettings["y"]))

        self.protocol("WM_DELETE_WINDOW", self.parent.closeOptionsMenu)
        label = Label(self, text="Menu options here")
        label.pack()

        settingsFrame = Frame(self, bg='white')

        settings = self.parent.settings.listSettings()

        i = 0
        self.setEntry = {}
        for k, v in settings.items():

            setLabel = Label(settingsFrame, text=k)
            self.setEntry[k] = Entry(settingsFrame)
            self.setEntry[k].insert(0,json.dumps(v).replace('"',''))
            setLabel.grid(row=i, column=0)
            self.setEntry[k].grid(row=i, column=1)

            i += 1

        settingsFrame.pack()

        #Make a file update button for every file in the settings:
        fileList = self.parent.settings.listFiles()

        for fileName in fileList:
            cmd = partial(self.updateFile, fileName)
            b = Button(self, text=fileName, command=cmd, anchor=N)
            b.pack()

        save = Button(self,text="Save", command=self.saveAndClose, anchor=N)
        save.pack()

    def updateFile(self, fileName):
        previousPath = Path(self.parent.settings.getFilePath(fileName))
        fileType = self.parent.settings.getFileType(fileName)
        if previousPath.exists():
            initial = previousPath.parent
        else:
            initial = "./"
        
        name = filedialog.askopenfilename(initialdir=initial, title="Select {}".format(fileName), filetypes = ((fileType, "*{}*".format(fileType)), ("all files", "*.*")))

        if name != "":
            filePath = Path(name)
            self.parent.settings.updateFileSettings(fileName, filePath)

    def saveAndClose(self):
        settings = {}
        for k, v in self.setEntry.items():
            settings[k] = v.get()

        self.parent.settings.modifySettings(settings)

        self.parent.log.reopenLogfile()

        self.parent.closeOptionsMenu()

class InventoryOverlay:
    #Overlays sit over inventory areas and highlight items. They also have the option of collecting inputs and passing 
    #information about them to the inventory module.
    def __init__(self, ui, x, y, w, h, cellGap, border, tabType):
        
        self.ui = ui
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cellGap = cellGap
        self.border = border
        self.tabType = tabType
        self.lines = {}
        self.clickThread = threading.Thread(target=self.trackClicks)
        self.trackClickThreadTerminate = False
        
        if tabType == "QuadStash":
            self.boxWidth = int((self.w - 2 * self.border - 23 * self.cellGap) / 24)
            self.boxHeight = int((self.h - 2 * self.border - 23 * self.cellGap) / 24)
        elif tabType == "PremiumStash" or tabType == "NormalStash":
            self.boxWidth = int((self.w - 2 * self.border - 11 * self.cellGap) / 12)
            self.boxHeight = int((self.h - 2 * self.border - 11 * self.cellGap) / 12)
        else:
            self.boxWidth = int((self.w - 2 * self.border - 11 * self.cellGap) / 12)
            self.boxHeight = int((self.h - 2 * self.border - 11 * self.cellGap) / 5)

        self.lineCanvas = Canvas(self.ui.canvas, width=self.w, height=self.h, bg='white', bd=0, highlightthickness=0)
        self.lineCanvas.place(x=self.x, y=self.y)

        self.clickThread.start()

    def trackClicks(self):
        state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
        
        while not self.trackClickThreadTerminate:
            a = win32api.GetKeyState(0x01)
            c = win32api.GetKeyState(win32con.VK_CONTROL)

            if a != state_left:  # Button state changed
                state_left = a
                _, _, (x, y) = win32gui.GetCursorInfo()
                if a < 0 and c < 0: 
                    #process a ctrl click at pixel x, y by translating into an x/y position in the tab and checking if it is in the cell gap
                    if x > self.x + self.border and x < self.x + self.w - self.border and y > self.y + self.border and y < self.y + self.h - self.border:
                        #get the x,y position within the overlay
                        xNorm = x - self.x - self.border
                        yNorm = y - self.y - self.border

                        #check if the click falls within a cell and not in a gap
                        if xNorm % (self.boxWidth + self.cellGap) < self.w and yNorm % (self.boxHeight + self.cellGap) < self.h:
                            xCell = xNorm // (self.boxWidth + self.cellGap)
                            yCell = yNorm // (self.boxHeight + self.cellGap)

                            #remove the highlight from the clicked item
                            self.removeHighlight(xCell, yCell)

                            #pass the click off to the inventory module for processing. Let inventory worry about if there is actually an item there or not
                            if self.tabType == "QuadStash" or self.tabType == "PremiumStash" or self.tabType == "NormalStash":
                                tab = self.ui.settings.currentSettings["Chaos"]["index"]
                                self.ui.inventory.clickFromStash(tab, xCell, yCell)
                            
                            #TODO:Add functionality for other tab types

    def highlightItems(self, itemList):
        self.lines = {}
        for item in itemList:
            self.addHighlight(item["x"],item["y"],item["w"],item["h"],item["color"])

    def addHighlight(self, x, y, w, h, color):
        
        itemKey = (x, y)
        itemLines = []

        self.removeHighlight(x, y)

        x1 = self.border + x * (self.boxWidth + self.cellGap)
        x2 = x1 + w * self.boxWidth + (w-1) * self.cellGap
        y1 = self.border + y * (self.boxHeight + self.cellGap)
        y2 = y1 + h * self.boxHeight + (h-1) * self.cellGap

        itemLines.append(self.lineCanvas.create_line(x1, y1, x1, y2, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x1, y1, x2, y1, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x1, y2, x2, y2, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x2, y1, x2, y2, fill=color, width=2.0, state=DISABLED))

        itemLines.append(self.lineCanvas.create_line(x1, y1, x1 + 10, y1 + 10, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x1, y2, x1 + 10, y2 - 10, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x2, y1, x2 - 10, y1 + 10, fill=color, width=2.0, state=DISABLED))
        itemLines.append(self.lineCanvas.create_line(x2, y2, x2 - 10, y2 - 10, fill=color, width=2.0, state=DISABLED))

        self.lines[itemKey] = itemLines

    def removeHighlight(self, x, y):
        chaosIndex = self.ui.settings.currentSettings["Chaos"]["index"]
        itemId = self.ui.inventory.stashFill[chaosIndex][x][y]
        
        if itemId != "":
            x = self.ui.inventory.stash[itemId]["x"]
            y = self.ui.inventory.stash[itemId]["y"]

        itemKey = (x, y)
        if itemKey in self.lines:
            for line in self.lines[itemKey]:
                self.lineCanvas.delete(line)
            self.lines.pop(itemKey)

    def destroy(self):
        self.trackClickThreadTerminate = True
        while self.clickThread.is_alive():
            time.sleep(0.1)
        self.lineCanvas.destroy()

class HUDOverlay:
    def __init__(self, ui, x, y, w, h, textCount, colors):
        self.ui = ui
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = []
        self.textCount = textCount
        self.colors = colors

        self.stringCanvas = Canvas(self.ui.canvas, width=self.w, height=self.h, bg='white', bd=0, highlightthickness=0)
        self.stringCanvas.place(x=self.x, y=self.y)

        for i in range(self.textCount):
            self.text.append(self.stringCanvas.create_text(int(i * self.w / self.textCount),0, anchor=NW, text="", font=("Courier", 16), fill=self.colors[i]))

    def updateText(self, text):
        strings = text.split(",")
        for i in range(self.textCount):
            self.stringCanvas.itemconfig(self.text[i],text=strings[i])
    
    def destroy(self):
        self.stringCanvas.destroy()
            
class ControlPannel(Toplevel):

    def __init__(self, master=None, parent=None):
        super().__init__(master=master)

        self.initControl(parent)

    def initControl(self, parent):

        self.parent = parent
        self.title = "Control Pannel"

        self.parent.character.registerUIUpdate(self.inventoryUpdated)

        windowSettings = self.parent.settings.getWindowSettings("Control")
        self.geometry("{}x{}+{}+{}".format(windowSettings["w"], windowSettings["h"], windowSettings["x"], windowSettings["y"]))

        self.protocol("WM_DELETE_WINDOW", self.parent.closeControlPannel)

        self.inventoryLabel = Label(self, text="Character Inventory Rankings")
        self.inventoryFrame = Frame(self,width=100, height=50, bg="white")
        self.inventoryButtons = []
        self.selectedItemStats = Label(self, text="")
        self.itemSearchFrame = Frame(self, bg="white")
        self.itemSearchTitles = []
        self.itemSearchButtons = []
        self.itemSearchGo = None
        self.itemSearch = {}

        for item, stats in self.parent.character.equippedItemStats.items():
            func = partial(self.inventoryItemSelect, item, stats)
            self.inventoryButtons.append(Button(self.inventoryFrame, text=item, command=func))
        
        self.redraw()

    def redraw(self):

        for button in self.inventoryButtons:
            button.place_forget()
        
        children = self.pack_slaves()
        for child in children:
            child.pack_forget()

        children = self.itemSearchFrame.grid_slaves()
        for child in children:
            child.grid_forget()

        self.inventoryLabel.pack()

        buttonCount = len(self.inventoryButtons)
        if buttonCount > 0:
            buttonWidth = 1.0 / buttonCount
        else:
            buttonWidth = 1.0

        for i in range(buttonCount):
            self.inventoryButtons[i].place(relheight=1.0,relwidth=0.98*buttonWidth,relx=buttonWidth*i)

        for i in range(len(self.itemSearchTitles)):
            self.itemSearchTitles[i].grid(row=i, column=0)
            for j in range(len(self.itemSearchButtons[i])):
                self.itemSearchButtons[i][j].grid(row=i, column=j+1)
        
        self.inventoryFrame.pack(fill=X)
        self.selectedItemStats.pack(fill=X)
        self.itemSearchFrame.pack(fill=BOTH, expand=True)
        if self.itemSearchGo != None:
            self.itemSearchGo.pack()
        
    def inventoryItemSelect(self, item, stats):

        for title in self.itemSearchTitles:
            title.destroy()
        for buttonList in self.itemSearchButtons:
            for button in buttonList:
                button.destroy()

        self.itemSearchTitles = []
        self.itemSearchButtons = []
        self.itemSearch = {"Slot": item}

        selectedItemStatText = item + ":    "
        for stat in stats:
            if "Score" not in stat and stats[stat] != 0:
                selectedItemStatText += "{}: {}    ".format(stat, stats[stat])
        
        selectedItemStatText = selectedItemStatText[:-4]

        self.selectedItemStats['text'] = selectedItemStatText

        #this is where the controls for searchable attributes is created
        searchableAttributes = [{"Name": "Total Life:", "Current": stats["Life"],"Start": 0, "Stop": 100, "Step": 10, "autoSelect": False, "Bases": "All"},
                                {"Name": "MoveSpeed:", "Current": 0,"Start": 0, "Stop": 30, "Step": 5, "autoSelect": False, "Bases": "Boots"},#Fix checking MS on items and then fix current
                                {"Name": "Eff Fire Resist:", "Current": self.parent.character.getEffectiveFireResist(item),"Start": 0, "Stop": 70, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Eff Cold Resist:", "Current": self.parent.character.getEffectiveColdResist(item),"Start": 0, "Stop": 70, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Eff Lightning Resist:", "Current": self.parent.character.getEffectiveLightningResist(item),"Start": 0, "Stop": 70, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Eff Chaos Resist:", "Current": stats["Chaos"],"Start": 0, "Stop": 50, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Eff Ele Resist:", "Current": self.parent.character.getEffectiveEleResist(item),"Start": 0, "Stop": 120, "Step": 10, "autoSelect": False, "Bases": "All"},
                                {"Name": "Eff Resist:", "Current": self.parent.character.getEffectiveResist(item),"Start": 0, "Stop": 120, "Step": 10, "autoSelect": False, "Bases": "All"},
                                {"Name": "Strength:", "Current": stats["Strength"],"Start": 0, "Stop": 50, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Dexterity:", "Current": stats["Dexterity"],"Start": 0, "Stop": 50, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Intelligence:", "Current": stats["Intelligence"],"Start": 0, "Stop": 50, "Step": 5, "autoSelect": False, "Bases": "All"},
                                {"Name": "Required Level:", "Current": self.parent.character.level,"Start": self.parent.character.level, "Stop": self.parent.character.level + 5, "Step": 1, "autoSelect": True, "Bases": "All"},
                                {"Name": "Required Str:", "Current": self.parent.character.charDefStats["Strength"],"Start": max(0,self.parent.character.charDefStats["Strength"]-25), "Stop": self.parent.character.charDefStats["Strength"]+25, "Step": 5, "autoSelect": True, "Bases": "All"},
                                {"Name": "Required Dex:", "Current": self.parent.character.charDefStats["Dexterity"],"Start": max(0,self.parent.character.charDefStats["Dexterity"]-25), "Stop": self.parent.character.charDefStats["Dexterity"]+25, "Step": 5, "autoSelect": True, "Bases": "All"},
                                {"Name": "Required Int:", "Current": self.parent.character.charDefStats["Intelligence"],"Start": max(0,self.parent.character.charDefStats["Intelligence"]-25), "Stop": self.parent.character.charDefStats["Intelligence"]+25, "Step": 5, "autoSelect": True, "Bases": "All"}
                                ]
        #TODO: Vary the searchable ranges (and gear scoring) for mods based on the available rolls for each slot - Also, add MS specifically for boots

        for search in searchableAttributes:
            if search["Bases"] == "All" or search["Bases"] == item:
                self.itemSearchTitles.append(Label(self.itemSearchFrame, text=search["Name"], bg="white"))
                
                self.itemSearchButtons.append([])
                count = (search["Stop"] - search["Start"])//search["Step"]

                for j in range(count):
                    value = search["Start"] + j * search["Step"]
                    buttonText = str(value)
                    onClick = partial(self.toggleSearchValue,search["Name"], value)
                    if j == (search["Current"] - search["Start"])//search["Step"]:
                        button = Button(self.itemSearchFrame, command=onClick, text=buttonText, bg="yellow")
                        self.itemSearchButtons[-1].append(button)
                        if search["autoSelect"]:
                            self.itemSearch[search["Name"]] = value
                            button.configure(relief=SUNKEN)
                    else:
                        self.itemSearchButtons[-1].append(Button(self.itemSearchFrame, command=onClick, text=buttonText))
        
        if self.itemSearchGo == None:
            self.itemSearchGo = Button(self, text="Search!",command=self.searchAPIRequest)

        self.redraw()

    def toggleSearchValue(self, name, value):
        if name in self.itemSearch and self.itemSearch[name] == value:
            self.itemSearch.pop(name)
        else:
            self.itemSearch[name] = value

        for i in range(len(self.itemSearchButtons)):
            for button in self.itemSearchButtons[i]:
                searchText = self.itemSearchTitles[i]['text']
                if searchText in self.itemSearch and button['text'] == str(self.itemSearch[searchText]):
                    button.configure(relief=SUNKEN)
                else:
                    button.configure(relief=RAISED)

        print(self.itemSearch)
        self.redraw()

    def inventoryUpdated(self):
        for title in self.itemSearchTitles:
            title.destroy()
        for buttonList in self.itemSearchButtons:
            for button in buttonList:
                button.destroy()

        for button in self.inventoryButtons:
            button.destroy()

        if self.itemSearchGo != None:
            self.itemSearchGo.destroy()
            self.itemSearchGo = None

        self.itemSearchTitles = []
        self.inventoryButtons = []

        for item, stats in self.parent.character.equippedItemStats.items():
            func = partial(self.inventoryItemSelect, item, stats)
            self.inventoryButtons.append(Button(self.inventoryFrame, text=item, command=func))
        
        self.redraw()
    
    def searchAPIRequest(self):
        print("Searching for: {}".format(self.itemSearch))
        tradeSearch = generateTradeSearchJSON(self.itemSearch)
        tradeURL = self.parent.api.tradeSearch(tradeSearch)
        print(tradeURL)
        webbrowser.open(tradeURL)

def generateTradeSearchJSON(itemSearch):
    typeFilterOptions = {"Gloves": "armour.gloves",
                         "Boots": "armour.Boots",
                         "Helm": "armour.helmet",
                         "BodyArmour": "armour.chest",
                         "Ring": "accessory.ring",
                         "Ring2": "accessory.ring",
                         "Amulet": "accessory.amulet",
                         "Belt": "accessory.belt",
                         "Offhand": "armour.shield",
                         "Gloves": "armour.gloves",
                         "Weapon": "weapon"}

    statReq = {"Gloves": True,
               "Boots": True,
               "Helm": True,
               "BodyArmour": True,
               "Ring": False,
               "Ring2": False,
               "Amulet": False,
               "Belt": False,
               "Offhand": True,
               "Gloves": True,
               "Weapon": True}
    
    typeFilter = typeFilterOptions[itemSearch["Slot"]]

    if statReq[itemSearch["Slot"]]:
        reqFilters = {"str": {"max": itemSearch["Required Str:"]},
                      "dex": {"max": itemSearch["Required Dex:"]},
                      "int": {"max": itemSearch["Required Int:"]},
                      "lvl": {"max": itemSearch["Required Level:"]}}
    else:
        reqFilters = {"lvl": {"max": itemSearch["Required Level:"]}}


    tradeSearch = {"query": {"status": {"option": "online"},
                             "stats": [{"type": "and", "filters": []},
                                       {"type": "weight", "value": {"min": 0}, "filters": []}
                                      ],
                             "filters": {"req_filters": {"filters": reqFilters
                                                        },
                                         "type_filters": {"filters":{"category":{"option": typeFilter}}}
                                        }
                            },
                   "sort": {"price": "asc"}
                  }
    
    if "Total Life:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_life", "value":{"min": itemSearch["Total Life:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_life", "disabled": True})

    if "Eff Fire Resist:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_fire_resistance", "value":{"min": itemSearch["Eff Fire Resist:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_fire_resistance", "disabled": True})
    
    if "Eff Cold Resist:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_cold_resistance", "value":{"min": itemSearch["Eff Cold Resist:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_cold_resistance", "disabled": True})

    if "Eff Lightning Resist:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_lightning_resistance", "value":{"min": itemSearch["Eff Lightning Resist:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_lightning_resistance", "disabled": True})

    if "Eff Chaos Resist:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_chaos_resistance", "value":{"min": itemSearch["Eff Chaos Resist:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_chaos_resistance", "disabled": True})

    if "Strength:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_strength", "value":{"min": itemSearch["Strength:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_strength", "disabled": True})

    if "Dexterity:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_dexterity", "value":{"min": itemSearch["Dexterity:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_dexterity", "disabled": True})

    if "Intelligence:" in itemSearch:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_intelligence", "value":{"min": itemSearch["Intelligence:"]}})
    else:
        tradeSearch["query"]["stats"][0]["filters"].append({"id":"pseudo.pseudo_total_intelligence", "disabled": True})

    if "Eff Ele Resist:" in itemSearch:
        tradeSearch["query"]["stats"][1]["value"]["min"] = itemSearch["Eff Ele Resist:"]
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_fire_resistance"})
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_cold_resistance"})
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_lightning_resistance"})
    else:
        tradeSearch["query"]["stats"][1]["disabled"] = True
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_fire_resistance"})
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_cold_resistance"})
        tradeSearch["query"]["stats"][1]["filters"].append({"id":"pseudo.pseudo_total_lightning_resistance"})

    return json.dumps(tradeSearch)