from tkinter import Tk, Canvas, Frame, Toplevel, Label, Entry, BOTH, Button, N, NW, LEFT, BOTTOM, X, Y, SUNKEN, RAISED, DISABLED
from functools import partial
import time
import json
import threading
import time
import win32api, win32gui, win32con

class UserInterface(Frame):

    def __init__(self, master, settings, inventory):
        super().__init__(master=master)

        self.initUI(settings, inventory)

    def initUI(self, settings, inventory):

        self.master.title("Overlay Frame")
        self.pack(fill=BOTH, expand=1)
        self.menu = None
        self.chaosOverlay = None
        self.settings = settings
        self.inventory = inventory

        self.x = 23
        self.y = 170

        self.w = 840
        self.h = 840

        self.canvas = Canvas(self, bd=-2)
        self.canvas.config(bg='white')
        self.canvas.pack(fill=BOTH, expand=1)

        self.menuButton = Button(self.canvas, text="Menu", command = self.optionsMenu, anchor=N)
        self.menuButton.place(x=self.winfo_screenwidth()/2 + 30, y=0)

        self.chaosButton = Button(self.canvas, text="Chaos", command=self.toggleChaosOverlay, anchor=N)
        self.chaosButton.place(x=self.winfo_screenwidth()/2 - 30, y=0)

        self.redraw()

    def redraw(self):
        return

    def optionsMenu(self):
        if self.menu == None:
            self.menu = SettingsMenu(self.master, self)
        else:
            self.closeOptionsMenu()
    
    def closeOptionsMenu(self):
        self.settings.updateWindowSettings("Menu", self.menu.winfo_width(), self.menu.winfo_height(), self.menu.winfo_x(), self.menu.winfo_y())
        self.menu.destroy()
        self.menu = None

    def toggleChaosOverlay(self):
        if self.chaosOverlay == None:
            settings = self.settings.getWindowSettings("Chaos")
            self.chaosOverlay = Overlay(self,settings["x"],settings["y"],settings["w"],settings["h"],settings["cellGap"],settings["border"],settings["tabType"])
            for i in range(24):
                self.chaosOverlay.addHighlight(i,i,1,1,"#90fc03")
        else:
            self.chaosOverlay.destroy()
            self.chaosOverlay = None

    def killAllThreads(self):
        if self.menu != None:
            self.menu.destroy()
        if self.chaosOverlay != None:
            self.chaosOverlay.destroy()

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

        save = Button(self,text="Save", command=self.saveAndClose, anchor=N)
        save.pack()

    def saveAndClose(self):
        settings = {}
        for k, v in self.setEntry.items():
            settings[k] = v.get()

        self.parent.settings.modifySettings(settings)

        self.parent.closeOptionsMenu()

class Overlay:
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

        self.lineCanvas = Canvas(ui.canvas, width=self.w, height=self.h, bg='white', bd=0, highlightthickness=0)
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
                        xNorm = x - self.x - self.border
                        yNorm = y - self.y - self.border
                        if xNorm % (self.boxWidth + self.cellGap) < self.w and yNorm % (self.boxHeight + self.cellGap) < self.h:
                            xCell = xNorm // (self.boxWidth + self.cellGap)
                            yCell = yNorm // (self.boxHeight + self.cellGap)

                            self.removeHighlight(xCell, yCell)
                            #TODO:***THIS IS WHERE YOU PUT THE CODE FOR CHANGING ITEMS IN THE INVENTORY MODULE***

    def highlightItems(self, itemList):
        self.lines = {}
        for item in itemList:
            self.addHighlight(item["y"],item["y"],item["w"],item["h"],item["color"])

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
