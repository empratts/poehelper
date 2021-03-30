from tkinter import Tk, Canvas, Frame, Toplevel, Label, Entry, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED, DISABLED, filedialog
from functools import partial
import time
import json
import threading
import time
from datetime import datetime
import win32api, win32gui, win32con
from pathlib import Path
from log import ReadLogFile

class UserInterface(Frame):

    def __init__(self, master, settings, inventory, api, chaos):
        super().__init__(master=master)

        self.initUI(settings, inventory, api, chaos)

    def initUI(self, settings, inventory, api, chaos):

        self.master.title("Overlay Frame")
        self.pack(fill=BOTH, expand=1)
        self.menu = None
        self.chaosOverlay = None
        self.mainOverlay = None
        self.vendorOverlay = None
        self.settings = settings
        self.inventory = inventory
        self.api = api
        self.chaos = chaos
        self.logFile = None
        self.currentLog = None #timestamp of when log was opened to make sure only 1 thread is trying to read the log at a time.
        self.hideout = False

        self.canvas = Canvas(self, bd=-2)
        self.canvas.config(bg='white')
        self.canvas.pack(fill=BOTH, expand=1)

        self.menuButton = Button(self.canvas, text="Menu", command = self.optionsMenu, anchor=N)
        self.menuButton.place(x=self.winfo_screenwidth()/2 + 30, y=0)

        self.chaosButton = Button(self.canvas, text="Chaos", command=self.toggleChaosOverlay, anchor=N)
        self.chaosButton.place(x=self.winfo_screenwidth()/2 - 30, y=0)

        self.updateButton = Button(self.canvas, text="update", command=self.updateStash, anchor=N)
        self.updateButton.place(x=self.winfo_screenwidth()/2 - 30, y=25)

        self.chaosHUD = None
        self.initChaosHUD()

        self.reopenLogfile()

        self.testReader = ReadLogFile(settings, self.master)
        self.testReader.registerCallback(self.callbackTest, ": You have entered ")
        self.testReader.reopenLogfile()

        self.redraw()

    def redraw(self):
        return

    def callbackTest(self, text):
        print("SUCCESS: " + text)

    #Proposed redsign of this whole process: readLogFile allows other modules to register other function/regex pairs
    #It just compares each logline to each regex and then if it matches, it passes the line to the associated function
    #This will simplify this module and allow the moving of the update stash and update chararacter functions to a more
    #appropriate place. Not currently sure where they belong, but it feels wrong having them in the UI module.
    #Possible locations include Inventory and Character modules. Inventory feels right ATM, as the update functions update the inventories
    #directly, and char/chaos can just pull from the Inventory to do thier analysis.
    #Also, the pulling of settings to pass to the API probably belongs in the API module...
    #actually, the whole thing is F'd... The triggers should be in the inventory module, and the bulk of the logic currently in the update functions
    #should be in the API module. Also, reading the log might belong in its own module
    def readLogFile(self, since):

        if since != self.currentLog:
            return

        if self.logFile is None:
            try:
                logPath = Path(self.settings.getFileSettings("logFile"))
                if logPath.suffix == ".txt" and logPath.exists():
                    self.logFile = open(logPath, "r", errors='ignore')
                    self.logFile.seek(0,2)
                else:
                    print("Invalid Logfile - incorrect file type or file does not exist")
                    return
            except IndexError:
                print("Invalid Logfile Name")
                return
            except Exception as err:
                print("Error opening log file", type(err), err)
                return
        
        logLines = self.logFile.readline()
        if len(logLines) > 0:
            if ": You have entered " in logLines and "Hideout." in logLines: #add more here for all towns. Also figure out what the game logs going in and out of the azurite mine
                if self.hideout:
                    #moving from one safe zone to another, inspect both stash and character
                    print("SUCCESS")
                    self.updateStash()
                    self.updateCharacter()
                else:
                    #moving from a non-stash zone to a safe zone, so only update the character
                    self.updateCharacter()

                self.enterHideout()

            elif ": You have entered " in logLines:
                if self.hideout:
                    #Leaving a safe zone, inspect the stash and character
                    self.updateStash()
                    self.updateCharacter()
                else:
                    #moving from a non-stash zone to another, only update the character
                    self.updateCharacter()

                for zone, level in self.settings.combatZones.items():
                    if zone in logLines:
                        print(zone, level)

                self.leaveHideout()
        
        call = lambda : self.readLogFile(since)
        self.master.after(100, call)

    def updateStash(self):
        #look for the chaos tab in the last place it was found
        league = self.settings.currentSettings["league"]
        tabIndex = self.settings.currentSettings["chaos"]["index"]
        account = self.settings.currentSettings["account"]
        POESESSID = self.settings.currentSettings["POESESSID"]

        tabName = self.settings.currentSettings["chaos"]["tab"]

        stash = self.api.updateStashTab(league, tabIndex, account, POESESSID)

        if stash != {}:
            for tab in stash["tabs"]:
                if tab["n"] == tabName:
                    if tab["i"] != tabIndex:
                        #the tab has moved in the stash. Update its index in the settings and request it at its new location.
                        tabIndex = tab["i"]
                        self.settings.updateWrappedSetting("chaos:index", tab["i"])
                        stash = self.api.updateStashTab(league, tab["i"], account, POESESSID)
                    break
        
        if stash != {}:
            chaosWindowSettings = self.settings.getWindowSettings("Chaos")
            for tab in stash["tabs"]:
                if tab["n"] == tabName and tab["i"] == tabIndex and tab["type"] != chaosWindowSettings["tabType"]:
                    self.settings.updateWrappedSetting("#Chaos:tabType", tab["type"])
                    self.settings.writeSettings()
                    break
    
            self.inventory.parseStash(stash, tabIndex)

            #Generate the string for the chaos HUD
            HUDString = self.chaos.getChaosHUDString()
            self.chaosHUD.updateText(HUDString)

    def updateCharacter(self):
        account = self.settings.currentSettings["account"]
        character = self.settings.currentSettings["character"]
        POESESSID = self.settings.currentSettings["POESESSID"]

        char = self.api.updateCharacter(account, character, POESESSID)

        if char != {}:
            self.inventory.parseCharacter(char)

    def reopenLogfile(self):
        if self.logFile is not None:
            self.logFile.close()
            self.logFile = None

        now = datetime.now()
        self.currentLog = now
        self.readLogFile(now)

    def optionsMenu(self):
        if self.menu is None:
            self.menu = SettingsMenu(self.master, self)
        else:
            self.closeOptionsMenu()
    
    def closeOptionsMenu(self):
        self.settings.updateWindowSettings("Menu", self.menu.winfo_width(), self.menu.winfo_height(), self.menu.winfo_x(), self.menu.winfo_y())
        self.menu.destroy()
        self.menu = None

    def initChaosHUD(self):
        settings = self.settings.getWindowSettings("ChaosHUD")
        self.chaosHUD = HUDOverlay(self,settings["x"],settings["y"],settings["w"],settings["h"],8, settings["colors"])

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

        logButton = Button(self, text="Log File", command=self.updateLogFile, anchor=N)
        logButton.pack()

        baseButton = Button(self, text="Base Filter", command=self.updateBaseFilter, anchor=N)
        baseButton.pack()

        activeButton = Button(self, text="Active Filter", command=self.updateActiveFilter, anchor=N)
        activeButton.pack()

        save = Button(self,text="Save", command=self.saveAndClose, anchor=N)
        save.pack()

    def updateLogFile(self):
        initial = self.parent.settings.getFileSettings("logFile")
        filePath = Path(filedialog.askopenfilename(initialdir=initial, title="Select PoE Log File", filetypes = (("Text files", "*.txt*"), ("all files", "*.*"))))
        self.parent.settings.updateFileSettings("logFile", filePath)

    def updateBaseFilter(self):
        initial = self.parent.settings.getFileSettings("baseFilter")
        filePath = Path(filedialog.askopenfilename(initialdir=initial, title="Select Base Filter", filetypes = (("Filter files", "*.filter*"), ("all files", "*.*"))))
        self.parent.settings.updateFileSettings("baseFilter", filePath)

    def updateActiveFilter(self):
        initial = self.parent.settings.getFileSettings("activeFilter")
        filePath = Path(filedialog.askopenfilename(initialdir=initial, title="Select Active Filter", filetypes = (("Filter files", "*.filter*"), ("all files", "*.*"))))
        self.parent.settings.updateFileSettings("activeFilter", filePath)

    def saveAndClose(self):
        settings = {}
        for k, v in self.setEntry.items():
            settings[k] = v.get()

        self.parent.settings.modifySettings(settings)

        self.parent.reopenLogfile()

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
                                tab = self.ui.settings.currentSettings["chaos"]["index"]
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
        chaosIndex = self.ui.settings.currentSettings["chaos"]["index"]
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
            self.text.append(self.stringCanvas.create_text(int(i * self.w / 8),0, anchor=NW, text="", font=("Courier", 16), fill=self.colors[i]))

    def updateText(self, text):
        strings = text.split(",")
        for i in range(self.textCount):
            self.stringCanvas.itemconfig(self.text[i],text=strings[i])
    
    def destroy(self):
        self.stringCanvas.destroy()
            