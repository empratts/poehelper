"""
Filter module updates from the base filter to the active filter in real time based on input from other modules.
Here we provide a framework for other modules (like Chaos and Character) to send info on items they want to be highlighted/hidden/ignored
Items not referenced or ignored by other modules will fall through to whatever the base filter shows.
"""

class Filter:
    def __init__(self, settings):
        self.settings = settings
        self.highlights = {}

    def addHighlight(self, requestingModuleName, filterString):
        self.highlights[requestingModuleName] = filterString
        self.updateActiveFilter()

    def removeHighlight(self, requestingModuleName):
        self.highlights.pop(requestingModuleName)
        self.updateActiveFilter()
    
    def updateActiveFilter(self):
        baseFilter = self.settings.getFileSettings("baseFilter")
        activeFilter = self.settings.getFileSettings("activeFilter")

        active = open(activeFilter, "w")

        for v in self.highlights.values():
            active.write(v)

        default = open(baseFilter, "r")

        for line in default:
            active.write(line)
