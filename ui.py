from tkinter import Tk, Canvas, Frame, Toplevel, Label, Entry, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED, DISABLED, filedialog
from functools import partial
import time
import json
import threading
import time
from datetime import datetime
import win32api, win32gui, win32con
from pathlib import Path
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

        windowSettings = self.parent.settings.getWindowSettings("Control")
        self.geometry("{}x{}+{}+{}".format(windowSettings["w"], windowSettings["h"], windowSettings["x"], windowSettings["y"]))

        self.protocol("WM_DELETE_WINDOW", self.parent.closeControlPannel)

        self.inventoryLabel = Label(self, text="Character Inventory Rankings")
        self.inventoryFrame = Frame(self,width=100, height=50, bg="white")
        self.inventoryButtons = []
        self.itemSearchFrame = Frame(self, bg="white")
        self.itemSearchTitles = []
        self.itemSearchButtons = []

        for i in range(12):
            func = partial(self.inventoryItemSelect, i)
            self.inventoryButtons.append(Button(self.inventoryFrame, text="Item {}".format(i), command=func))

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
        buttonWidth = 1.0 / buttonCount

        for i in range(buttonCount):
            self.inventoryButtons[i].place(relheight=1.0,relwidth=0.98*buttonWidth,relx=buttonWidth*i)

        for i in range(len(self.itemSearchTitles)):
            self.itemSearchTitles[i].grid(row=i, column=0)
            for j in range(len(self.itemSearchButtons[i])):
                self.itemSearchButtons[i][j].grid(row=i, column=j+1)
        
        self.inventoryFrame.pack(fill=X)
        self.itemSearchFrame.pack(fill=BOTH, expand=True)
        
    def inventoryItemSelect(self, item):
        for title in self.itemSearchTitles:
            title.destroy()
        for buttonList in self.itemSearchButtons:
            for button in buttonList:
                button.destroy()

        self.itemSearchTitles = []
        self.itemSearchButtons = []

        for i in range(3):
            self.itemSearchTitles.append(Label(self.itemSearchFrame, text="Item {}, Attr {}".format(item, i)))
            self.itemSearchButtons.append([])
            for j in range(10):
                self.itemSearchButtons[i].append(Button(self.itemSearchFrame, text="{}-{}".format(10 * j + 1, 10 * j + 10)))
        
        self.redraw()