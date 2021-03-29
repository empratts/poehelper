"""
Chaos module looks at the inventory and suggests sets of items to vendor
"""

itemClassMap = {"Weapon":["Driftwood Club","Tribal Club","Spiked Club","Petrified Club","Barbed Club","Flanged Mace","Ancestral Club","Tenderizer","Rusted Sword","Copper Sword","Sabre","Variscite Blade","Cutlass","Gemstone Sword","Corsair Sword","Glass Shank","Skinning Knife","Stiletto","Flaying Knife","Prong Dagger","Poignard","Golden Kris","Trisula","Gutting Knife","Ambusher","Sai","Carving Knife","Boot Knife","Copper Kris","Skean","Imp Dagger","Butcher Knife","Boot Blade","Royal Skean","Fiend Dagger","Slaughter Knife","Ezomyte Dagger","Platinum Kris","Imperial Skean","Demon Dagger","Driftwood Wand","Goat's Horn","Carved Wand","Quartz Wand","Spiraled Wand","Sage Wand","Pagan Wand","Faun's Horn","Engraved Wand","Crystal Wand","Serpent Wand","Omen Wand","Heathen Wand","Demon's Horn","Imbued Wand","Opal Wand","Tornado Wand","Prophecy Wand","Profane Wand","Convoking Wand","Driftwood Sceptre"],
                "Body"  :["Plate Vest","Chestplate","Copper Plate","War Plate","Full Plate","Arena Plate","Lordly Plate","Bronze Plate","Battle Plate","Sun Plate","Colosseum Plate","Majestic Plate","Golden Plate","Crusader Plate","Astral Plate","Gladiator Plate","Glorious Plate","Shabby Jerkin","Strapped Leather","Buckskin Tunic","Wild Leather","Full Leather","Sun Leather","Thief's Garb","Eelskin Tunic","Frontier Leather","Glorious Leather","Coronal Leather","Cutthroat's Garb","Sharkskin Tunic","Destiny Leather","Exquisite Leather","Zodiac Leather","Assassin's Garb","Simple Robe","Silken Vest","Scholar's Robe","Silken Garb","Mage's Vestment","Silk Robe","Cabalist Regalia","Sage's Robe","Silken Wrap","Conjurer's Vestment","Spidersilk Robe","Destroyer Regalia","Savant's Robe","Necromancer Silks","Occultist's Vestment","Widowsilk Robe","Vaal Regalia","Scale Vest","Light Brigandine","Scale Doublet","Infantry Brigandine","Full Scale Armour","Soldier's Brigandine","Field Lamellar","Wyrmscale Doublet","Hussar Brigandine","Full Wyrmscale","Commander's Brigandine","Battle Lamellar","Dragonscale Doublet","Desert Brigandine","Full Dragonscale","General's Brigandine","Triumphant Lamellar","Chainmail Vest","Chainmail Tunic","Ringmail Coat","Chainmail Doublet","Full Ringmail","Full Chainmail","Holy Chainmail","Latticed Ringmail","Crusader Chainmail","Ornate Ringmail","Chain Hauberk","Devout Chainmail","Loricated Ringmail","Conquest Chainmail","Elegant Ringmail","Saint's Hauberk","Saintly Chainmail","Padded Vest","Oiled Vest","Padded Jacket","Oiled Coat","Scarlet Raiment","Waxed Garb","Bone Armour","Quilted Jacket","Sleek Coat","Crimson Raiment","Lacquered Garb","Crypt Armour","Sentinel Jacket","Varnished Coat","Blood Raiment","Sadist Garb","Carnal Armour"],
                "Helm"  :["Iron Hat","Cone Helmet","Barbute Helmet","Close Helmet","Gladiator Helmet","Reaver Helmet","Siege Helmet","Samite Helmet","Ezomyte Burgonet","Royal Burgonet","Eternal Burgonet","Leather Cap","Tricorne","Leather Hood","Wolf Pelt","Hunter Hood","Noble Tricorne","Ursine Pelt","Silken Hood","Sinner Tricorne","Lion Pelt","Vine Circlet","Iron Circlet","Torture Cage","Tribal Circlet","Bone Circlet","Lunaris Circlet","Steel Circlet","Necromancer Circlet","Solaris Circlet","Mind Cage","Hubris Circlet","Battered Helm","Sallet","Visored Sallet","Gilded Sallet","Secutor Helm","Fencer Helm","Lacquered Helmet","Fluted Bascinet","Pig-Faced Bascinet","Nightmare Bascinet","Rusted Coif","Soldier Helmet","Great Helmet","Crusader Helmet","Aventail Helmet","Zealot Helmet","Great Crown","Magistrate Crown","Prophet Crown","Praetor Crown","Bone Helmet","Scare Mask","Plague Mask","Iron Mask","Festival Mask","Golden Mask","Raven Mask","Callous Mask","Regicide Mask","Harlequin Mask","Vaal Mask","Deicide Mask"],
                "Glove" :["Iron Gauntlets","Plated Gauntlets","Bronze Gauntlets","Steel Gauntlets","Antique Gauntlets","Ancient Gauntlets","Goliath Gauntlets","Vaal Gauntlets","Titan Gauntlets","Spiked Gloves","Rawhide Gloves","Goathide Gloves","Deerskin Gloves","Nubuck Gloves","Eelskin Gloves","Sharkskin Gloves","Shagreen Gloves","Stealth Gloves","Gripped Gloves","Slink Gloves","Wool Gloves","Velvet Gloves","Silk Gloves","Embroidered Gloves","Satin Gloves","Samite Gloves","Conjurer Gloves","Arcanist Gloves","Sorcerer Gloves","Fingerless Silk Gloves","Fishscale Gauntlets","Ironscale Gauntlets","Bronzescale Gauntlets","Steelscale Gauntlets","Serpentscale Gauntlets","Wyrmscale Gauntlets","Hydrascale Gauntlets","Dragonscale Gauntlets","Chain Gloves","Ringmail Gloves","Mesh Gloves","Riveted Gloves","Zealot Gloves","Soldier Gloves","Legion Gloves","Crusader Gloves","Wrapped Mitts","Strapped Mitts","Clasped Mitts","Trapper Mitts","Ambush Mitts","Carnal Mitts","Assassin's Mitts","Murder Mitts"],
                "Boot"  :["Iron Greaves","Steel Greaves","Plated Greaves","Reinforced Greaves","Antique Greaves","Ancient Greaves","Goliath Greaves","Vaal Greaves","Titan Greaves","Rawhide Boots","Goathide Boots","Deerskin Boots","Nubuck Boots","Eelskin Boots","Sharkskin Boots","Shagreen Boots","Stealth Boots","Slink Boots","Wool Shoes","Velvet Slippers","Silk Slippers","Scholar Boots","Satin Slippers","Samite Slippers","Conjurer Boots","Arcanist Slippers","Sorcerer Boots","Leatherscale Boots","Ironscale Boots","Bronzescale Boots","Steelscale Boots","Serpentscale Boots","Wyrmscale Boots","Hydrascale Boots","Dragonscale Boots","Two-Toned Boots","Chain Boots","Ringmail Boots","Mesh Boots","Riveted Boots","Zealot Boots","Soldier Boots","Legion Boots","Crusader Boots","Wrapped Boots","Strapped Boots","Clasped Boots","Shackled Boots","Trapper Boots","Ambush Boots","Carnal Boots","Assassin's Boots","Murder Boots"],
                "Belt"  :["Chain Belt","Rustic Sash","Stygian Vise","Heavy Belt","Leather Belt","Cloth Belt","Studded Belt","Vanguard Belt","Crystal Belt"],
                "Amulet":["Coral Amulet","Paua Amulet","Amber Amulet","Jade Amulet","Lapis Amulet","Gold Amulet","Agate Amulet","Citrine Amulet","Turquoise Amulet","Onyx Amulet","Marble Amulet","Blue Pearl Amulet"],
                "Ring"  :["Coral Ring","Iron Ring","Paua Ring","Unset Ring","Sapphire Ring","Topaz Ring","Ruby Ring","Diamond Ring","Gold Ring","Moonstone Ring","Two-Stone Ring","Amethyst Ring","Prismatic Ring", "Cerulean Ring", "Opal Ring", "Vermillion Ring"]}

itemSizeMap = { "Weapon":{"w":1, "h":3},
                "Body"  :{"w":2, "h":3},
                "Helm"  :{"w":2, "h":2},
                "Glove" :{"w":2, "h":2},
                "Boot"  :{"w":2, "h":2},
                "Belt"  :{"w":2, "h":1},
                "Amulet":{"w":1, "h":1},
                "Ring"  :{"w":1, "h":1}}

requirements = [ "Weapon", "Weapon", "Body", "Helm", "Glove", "Boot", "Belt", "Amulet", "Ring", "Ring"]

class Chaos:

    def __init__(self, settings, inventory):
        self.settings = settings
        self.inventory = inventory

    def getChaosSet(self):
        inventoryId = "Stash" + str(1 + self.settings.currentSettings["chaos"]["index"])

        lowItems = {"Weapon":[],
                    "Body"  :[],
                    "Helm"  :[],
                    "Glove" :[],
                    "Boot"  :[],
                    "Belt"  :[],
                    "Amulet":[],
                    "Ring"  :[]}
        
        highItems = {"Weapon":[],
                     "Body"  :[],
                     "Helm"  :[],
                     "Glove" :[],
                     "Boot"  :[],
                     "Belt"  :[],
                     "Amulet":[],
                     "Ring"  :[]}

        for itemId, item in self.inventory.stash.items():

            if item["inventoryId"] == inventoryId and item["frameType"] == 2 and len(item["sockets"]) <= 5:

                #add it to the list of usable items
                if not item["identified"]: #Can change this later to allow for the option to do id'd chaos recipe
                    for slot in itemClassMap:
                        if itemSizeMap[slot]["w"] == item["w"] and itemSizeMap[slot]["h"] == item["h"]:
                            for base in itemClassMap[slot]:
                                if base in item["typeLine"]:
                                    if 60 <= item["ilvl"] < 75:
                                        lowItems[slot].append(itemId)
                                    elif item["ilvl"] > 75:
                                        highItems[slot].append(itemId)
        
        if self.settings.currentSettings["chaos"]["preserve_low_level"]:
            return self.buildSetPreserve(lowItems, highItems)
        else:
            return self.buildSet(lowItems, highItems)

    def buildSet(self, lowItems, highItems):
        requirementCounter = requirements.copy()
        highReqMissing = []
        itemSet = []

        highMissingSearch = {}

        for slot in highItems:
            highMissingSearch[slot] = highItems[slot].copy()

        #check for missing high level requirements
        for req in requirementCounter:
            if highMissingSearch[req] == []:
                highReqMissing.append(req)
            else:
                highMissingSearch[req].pop()

        #fill all slots that are missing high level items with low level ones.
        #if no high level slots are missing, take the first low lvl item available.
        if highReqMissing != []:
            for req in highReqMissing:
                if lowItems[req] == []:
                    return []
                print("Adding low item for missing slot {}".format(req))
                itemSet.append(lowItems[req].pop())
                requirementCounter.remove(req)
        else:
            for slot in lowItems:
                if lowItems[slot] != []:
                    print("Adding low item for non-missing slot {}".format(req))
                    itemSet.append(lowItems[slot].pop())
                    requirementCounter.remove(slot)
                    break
            else:
                return []
        
        #fill all remaining slots with high level items
        for req in requirementCounter:
            print("Adding high item for slot {}".format(req))
            itemSet.append(highItems[req].pop())

        return itemSet
    
    def buildSetPreserve(self, lowItems, highItems):
        requirementCounter = requirements.copy()
        highReqMissing = ""
        itemSet = []

        highMissingSearch = highItems.copy()

        #check for slots with no high level items
        for req in requirementCounter:
            if highMissingSearch[req] == []:
                if highReqMissing != "":
                    return []
                highReqMissing = req
            else:
                highMissingSearch[req] = highMissingSearch[req][:-1]

        #take a low level item, either to fill the slot with no high level items, or if no slots are missing high lvl items, take the frist available 
        if highReqMissing == "":
            #no high lvl requirements are missing, take the first low level requirement
            for slot in lowItems:
                if lowItems[slot] != []:
                    itemSet.append(lowItems[slot].pop())
                    requirementCounter.remove(slot)
                    break
        else:
            #take a low level item in the slot where the high level item is missing
            if lowItems[highReqMissing] == []:
                return []
            itemSet.append(lowItems[highReqMissing].pop())
            requirementCounter.remove(highReqMissing)

        #fill all remaining slots with high level items
        for req in requirementCounter:
            itemSet.append(highItems[req].pop())

        return itemSet
    
    def getChaosHUDString(self):
        inventoryId = "Stash" + str(1 + self.settings.currentSettings["chaos"]["index"])

        lowItems = {"Weapon":[],
                    "Body"  :[],
                    "Helm"  :[],
                    "Glove" :[],
                    "Boot"  :[],
                    "Belt"  :[],
                    "Amulet":[],
                    "Ring"  :[]}
        
        highItems = {"Weapon":[],
                     "Body"  :[],
                     "Helm"  :[],
                     "Glove" :[],
                     "Boot"  :[],
                     "Belt"  :[],
                     "Amulet":[],
                     "Ring"  :[]}

        for itemId, item in self.inventory.stash.items():

            if item["inventoryId"] == inventoryId and item["frameType"] == 2 and len(item["sockets"]) <= 5:

                #add it to the list of usable items
                if not item["identified"]: #Can change this later to allow for the option to do unid'd chaos recipe
                    for slot in itemClassMap:
                        if itemSizeMap[slot]["w"] == item["w"] and itemSizeMap[slot]["h"] == item["h"]:
                            for base in itemClassMap[slot]:
                                if base in item["typeLine"]:
                                    if 60 <= item["ilvl"] < 75:
                                        lowItems[slot].append(itemId)
                                    elif item["ilvl"] > 75:
                                        highItems[slot].append(itemId)
        
        HUDString = ""

        for slot in highItems:
            HUDString += "{}:{}/{},".format(slot[:2], len(highItems[slot]), len(lowItems[slot]))
        
        return HUDString