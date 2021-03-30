"""
Character module allows for character tracking and planning.
-Monitors levels vs current zone to ensure you are not wasting time killing during leveling
-Tracks gems/sockets compared to a plan to give reminders to fix sockets/gems
-Tracks flasks compared to levels
-Tracks life/damage/resists and makes suggestions (trade links) on upgrades
-Tracks currency income vs what you plan to buy during leveling and recommends what to pick up/sell
-MODIFIES THE LOOT FILTER IN REAL TIME based on the above suggestions
"""

class Character():
    def __init__(self, inventory, log):
        self.inventory = inventory
        self.log = log

        self.log.registerCallback(self.logCallback, ": You have entered")
    
    def logCallback(self, text):
        pass