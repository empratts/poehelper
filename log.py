from pathlib import Path
from datetime import datetime
import re


class ReadLogFile:

    def __init__(self, master, settings):
        self.settings = settings
        self.master = master
        self.since = None
        self.logFile = None
        self.currentLog = datetime.now() #timestamp of when log was opened to make sure only 1 thread is trying to read the log at a time.
        self.callbacks = {}
    
    def reopenLogfile(self):
        if self.logFile is not None:
            self.logFile.close()
            self.logFile = None

        now = datetime.now()
        self.currentLog = now
        self.readLogFile(now)
    
    #registers a callback function that will be called when pattern is matched in the logfile
    #function must accept a single argument (the string representation of the log line)
    def registerCallback(self, function, pattern):
        self.callbacks[function] = pattern

    def readLogFile(self, since):

        if since != self.currentLog:
            return

        if self.logFile is None:
            try:
                logPath = Path(self.settings.getFilePath("logFile"))
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
        
        while True:
            logLines = self.logFile.readline()

            if logLines == "":
                break

            for function, pattern in self.callbacks.items():
                match = re.search(pattern, logLines)
                if match is not None:
                    function(logLines)

        call = lambda : self.readLogFile(since)
        self.master.after(100, call)