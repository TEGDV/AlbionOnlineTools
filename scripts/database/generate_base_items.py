import json

def get_base_name(full_name):
    prefixes = ["Novice's", "Journeyman's", "Adept's", "Expert's", "Master's", "Grandmaster's", "Elder's"]
    for prefix in prefixes:
        if full_name.startswith(prefix + " "):
            return full_name[len(prefix) + 1:]
    return full_name

def get_category(base_code):
    bc = base_code.upper()
    if "ARMOR" in bc: return "Chest"
    if "SHOES" in bc: return "Feet"
    if "HEAD" in bc: return "Head"
    if "CAPE" in bc: return "Cape"
    if bc.startswith("OFF_"): return "Off-Hand"
    if "BAG" in bc: return "Bag"
    if "TOOL" in bc: return "Tool"
    return "Weapon"

def get_subcategory(base_code, category, name):
    bc = base_code.upper()
    n = name.upper()
    if category in ["Chest", "Head", "Feet"]:
        if "PLATE" in bc: return "Plate"
        if "LEATHER" in bc: return "Leather"
        if "CLOTH" in bc: return "Cloth"
        return None
    elif category == "Weapon":
        if "BLACK HANDS" in n: return "Other"
        
        if "QUARTERSTAFF" in n or "DOUBLE BLADED" in n or "IRON-CLAD" in n or "BLACK MONK" in n or "GRAILSEEKER" in n or "SOULSCYTHE" in n or "STAFF OF BALANCE" in n or "TWINBLADE" in n: return "Quarterstaff"
        if "SHAPESHIFTER" in n or "BLOODMOON" in n or "PROWLING" in n or "PRIMAL" in n or "ROOTBOUND" in n or "EARTHRUNE" in n or "HELLSPAWN" in n or "LIGHTCALLER" in n: return "Shapeshifter Staff"
        if "SWORD" in n or "CLAYMORE" in n or "SCIMITAR" in n or "BLADE" in n or "KINGMAKER" in n or "BROADSWORD" in n or "GALATINE" in n or "CLARENT" in n or "CARVING" in n: return "Sword"
        if "AXE" in n or "HALBERD" in n or "SCYTHE" in n or "CARRION" in n or "BEAR PAWS" in n or "REALMBREAKER" in n: return "Axe"
        if "MACE" in n or "MORNING STAR" in n or "FLAIL" in n or "INCUBUS" in n or "CAMLANN" in n or "OATHKEEPER" in n or "DREADSTORM" in n: return "Mace"
        if "NATURE STAFF" in n or "WILD STAFF" in n or "BLIGHT" in n or "DRUIDIC" in n or "RAMPANT" in n or "IRONROOT" in n or "FORGEBARK" in n: return "Nature Staff"
        if "HAMMER" in n or "POLEHAMMER" in n or "GROVEKEEPER" in n or "TOMBHAMMER" in n or "FORGE" in n: return "Hammer"
        if "GLOVE" in n or "BRAWLER" in n or "AVENTURA" in n or "CESTUS" in n or "FIST" in n or "HANDS" in n or "KNUCKLE" in n or "BRACERS" in n or "MAULERS" in n or " PIKE " in n or "SPIKED" in n: return "War Gloves"

        if "CROSSBOW" in n or "REPEATER" in n or "BOLTCASTERS" in n or "WEEPING" in n or "SIEGEBOW" in n or "ENERGY SHAPER" in n: return "Crossbow"
        if "BOW" in n and "CROSSBOW" not in n: return "Bow"
        if "DAGGER" in n or "CLAW" in n or "BLOODLETTER" in n or "FANG" in n or "DEATHGIVERS" in n or "BRIDLED" in n or "TWIN SLAYERS" in n: return "Dagger"
        if "SPEAR" in n or " PIKE" in n or "GLAIVE" in n or "LANCE" in n or "HERON" in n or "HARPOON" in n or "TRINITY" in n or "SPIRITHUNTER" in n or "DAYBREAKER" in n: return "Spear"

        if "FIRE STAFF" in n or "INFERNAL STAFF" in n or "IGNEOUS" in n or "BLAZING" in n or "WILDFIRE" in n or "BRIMSTONE" in n or "DAWN" in n or "FLAMEWALKER" in n: return "Fire Staff"
        if "HOLY STAFF" in n or "FALLEN" in n or "HALLOWFALL" in n or "LIFETOUCH" in n or "DIVINE" in n or "REDEMPTION" in n: return "Holy Staff"
        if "FROST STAFF" in n or " ICE " in n or "GLACIAL" in n or "HOARFROST" in n or "ICICLE" in n or "CHILLHOWL" in n or "PERMAFROST" in n or "ARCTIC" in n: return "Frost Staff"
        if "ARCANE" in n or "ENIGMATIC" in n or "OCCULT" in n or "EVENSPOKE" in n or "WITCHWORK" in n or "LOCUS" in n or "ASTRAL" in n or "EVENSONG" in n: return "Arcane Staff"
        if "CURSED STAFF" in n or "DEMONIC" in n or "SKULL" in n or "SHADOWCALLER" in n or "DAMNATION" in n or "LIFEGURSE" in n: return "Cursed Staff"

        if "SHAPESHIFTER" in bc: return "Shapeshifter Staff"
        if "FIRE" in bc or "INFERNO" in bc: return "Fire Staff"
        if "HOLY" in bc: return "Holy Staff"
        if "FROST" in bc or "ICE" in bc: return "Frost Staff"
        if "NATURE" in bc: return "Nature Staff"
        if "CURSE" in bc or "DEMON" in bc: return "Cursed Staff"
        if "ARCANE" in bc: return "Arcane Staff"
        if "KNUCKLE" in bc: return "War Gloves"
        if "CROSSBOW" in bc: return "Crossbow"
        if "BOW" in bc and "CROSSBOW" not in bc: return "Bow"
        if "SWORD" in bc: return "Sword"
        if "AXE" in bc or "SCYTHE" in bc: return "Axe"
        if "MACE" in bc: return "Mace"
        if "HAMMER" in bc: return "Hammer"
        if "DAGGER" in bc: return "Dagger"
        if "SPEAR" in bc or "GLAIVE" in bc: return "Spear"
        if "QUARTERSTAFF" in bc or "DOUBLEBLADEDSTAFF" in bc: return "Quarterstaff"
        return "Other"
        
    elif category == "Off-Hand":
        if "SHIELD" in n or "SARCOPHAGUS" in n or "CAITIFF" in n or "FACEBREAKER" in n or "AEGIS" in n: return "Warrior"
        if "TORCH" in n or "MISTCALLER" in n or "LEERING" in n or "CRYPTCANDLE" in n or "SCEPTER" in n: return "Hunter"
        if "TOME" in n or "EYE OF SECRETS" in n or "MUISAK" in n or "TAPROOT" in n or "CENSER" in n: return "Mage"
        
        if "SHIELD" in bc: return "Warrior"
        if "TORCH" in bc or "HORN" in bc or "CANE" in bc or "LAMP" in bc: return "Hunter"
        if "BOOK" in bc or "ORB" in bc or "SKULL" in bc or "TOTEM" in bc or "TALISMAN" in bc or "CENSER" in bc: return "Mage"
        
        return "Other"
    
    return None

import glob

def main():
    recipes = {}
    for filepath in glob.glob("data/recipes_*.json"):
        with open(filepath, "r") as f:
            cat_recipes = json.load(f)
            if isinstance(cat_recipes, dict):
                recipes.update(cat_recipes)
        
    with open("data/items.json", "r") as f:
        items = json.load(f)
        
    # Create mapping of base_code -> first item that matches to extract name
    base_codes_needed = set()
    for req in recipes.keys():
        parts = req.split('_', 1)
        if len(parts) == 2:
            base_codes_needed.add(parts[1])
            
    base_items_dict = {}
    
    # Try direct match first
    for item in items:
        uname = item.get("UniqueName", "")
        if "@" in uname: continue
        
        parts = uname.split('_', 1)
        if len(parts) == 2:
            bc = parts[1]
            if bc in base_codes_needed and bc not in base_items_dict:
                # Get name
                fname = item.get("LocalizedNames", {}).get("EN-US", uname)
                cat = get_category(bc)
                subcat = get_subcategory(bc, cat, fname)
                if subcat == "Other": continue
                base_items_dict[bc] = {
                    "base_code": bc,
                    "name": get_base_name(fname),
                    "category": cat,
                    "subcategory": subcat
                }

    # For any missing base codes, we might need to match with _AVALON etc.
    missing = base_codes_needed - set(base_items_dict.keys())
    for bc in missing:
        # Search items that START with T4_ + bc
        for item in items:
            uname = item.get("UniqueName", "")
            if "@" in uname: continue
            if uname.startswith(f"T4_{bc}"):
                fname = item.get("LocalizedNames", {}).get("EN-US", uname)
                cat = get_category(bc)
                subcat = get_subcategory(bc, cat, fname)
                if subcat == "Other": continue
                base_items_dict[bc] = {
                    "base_code": bc,
                    "name": get_base_name(fname),
                    "category": cat,
                    "subcategory": subcat
                }
                break

    # If still missing, just use base_code as name
    still_missing = base_codes_needed - set(base_items_dict.keys())
    for bc in still_missing:
        cat = get_category(bc)
        name = bc.replace("_", " ").title()
        subcat = get_subcategory(bc, cat, name)
        if subcat == "Other": continue
        base_items_dict[bc] = {
            "base_code": bc,
            "name": name,
            "category": cat,
            "subcategory": subcat
        }
                
    result = list(base_items_dict.values())
    result = sorted(result, key=lambda x: (x["category"], x["name"]))
    
    with open("data/base_craftable_items.json", "w") as f:
        json.dump(result, f, indent=2)
        
    print(f"Saved {len(result)} base items. Needed {len(base_codes_needed)}")

if __name__ == "__main__":
    main()
