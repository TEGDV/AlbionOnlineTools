import urllib.request
import json
import os
import re

URL = "https://raw.githubusercontent.com/broderickhyman/ao-bin-dumps/master/items.json"

def get_category(unique_name):
    base_code = unique_name
    if unique_name.startswith("T") and "_" in unique_name:
        parts = unique_name.split("_", 1)
        if len(parts) == 2:
            base_code = parts[1]
    
    bc = base_code.upper()
    
    # EXCLUSION LIST: Filter out non-equipment craftables
    exclusions = ["ARTEFACT", "FARM", "MOUNT", "TOKEN", "ESSENCE", "RUNE", "SOUL", "RELIC", "ALCOHOL", "POTION", "MEAL", "BREAD", "BUTTER", "MEAT", "FISHINGBAIT", "FURNITURE", "HELLGATE", "RANDOM_DUNGEON", "BACKPACK", "TRASH", "SHARD"]
    if any(ex in bc for ex in exclusions):
        return None
        
    # Exclude raw materials and refined materials
    materials = ["WOOD", "PLANKS", "ORE", "METALBAR", "ROCK", "STONEBLOCK", "HIDE", "LEATHER", "FIBER", "CLOTH"]
    # Check if exact match or _LEVEL match
    if bc in materials or any(bc.startswith(mat + "_LEVEL") for mat in materials):
        return None
        
    if "ARMOR" in bc: return "Chest"
    if "SHOES" in bc: return "Feet"
    if "HEAD" in bc: return "Head"
    if "CAPE" in bc: return "Cape"
    if "OFF" in bc or "SHIELD" in bc or "BOOK" in bc or "HORN" in bc or "TOTEM" in bc or "ORB" in bc or "TORCH" in bc or "CENSER" in bc or "CHALICE" in bc or "LAMP" in bc or "MISTCALLER" in bc or "CANE" in bc or "ROOT" in bc or "TAPESTRY" in bc or "ASTRAL" in bc: return "Off-Hand"
    if "BAG" in bc: return "Bag"
    if "TOOL" in bc: return "Tool"
    
    # Only return Weapon if it's explicitly a weapon (MAIN or 2H) and NOT a tool
    if ("MAIN" in bc or "2H" in bc) and "TOOL" not in bc:
        return "Weapon"
        
    return None

def parse_craft_resource(resource):
    if not resource: return []
    if isinstance(resource, dict):
        resource = [resource]
    reqs = []
    for r in resource:
        if "@uniquename" in r and "@count" in r:
            reqs.append({
                "UniqueName": r["@uniquename"],
                "count": int(r["@count"])
            })
    return reqs

def extract_tier(unique_name):
    m = re.match(r'^T(\d+)_', unique_name)
    if m:
        return int(m.group(1))
    return 1

def main():
    print("Downloading massive items.json dump...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        raw_data = json.loads(response.read().decode())
    print("Download complete.")
    
    recipes_by_cat = {}
    
    items = raw_data.get("items", {})
    for section_name, section_items in items.items():
        if section_name.startswith("@"): continue
        if not isinstance(section_items, list):
            section_items = [section_items]
            
        for item in section_items:
            if not isinstance(item, dict): continue
            
            uname = item.get("@uniquename", "")
            if not uname: continue
            
            # Skip enchanted variations since we compute them via enchant materials.
            # Wait, do we want to skip them? The current API subtracts 1 and adds enchant mats.
            # But the raw dump has the actual recipes for enchanted gear (e.g. T4_MAIN_FIRESTAFF@1 requires T4_PLANKS_LEVEL1).
            # Actually, the user's current recipe.json ONLY has base items (like T4_MAIN_FIRESTAFF)
            # and the `enchanting_route` calculates everything. We should ONLY store the BASE item recipes (no @ level).
            if "@" in uname: continue
            
            # Only care about T4 to T8
            if not uname.startswith("T4_") and not uname.startswith("T5_") and not uname.startswith("T6_") and not uname.startswith("T7_") and not uname.startswith("T8_"):
                continue
                
            craft_req = item.get("craftingrequirements")
            if not craft_req: continue
            
            # craftingrequirements could be a dict or a list (multiple ways to craft)
            if isinstance(craft_req, list):
                # Typically the first one is the standard craft, second might be royal or alternative?
                # We'll take the first one that has craftresource
                req_obj = None
                for c in craft_req:
                    if "craftresource" in c:
                        req_obj = c
                        break
                craft_req = req_obj
                
            if not craft_req or "craftresource" not in craft_req: continue
            
            resources = parse_craft_resource(craft_req["craftresource"])
            if not resources: continue
            
            category = get_category(uname)
            if not category: continue
            
            if category not in recipes_by_cat:
                recipes_by_cat[category] = {}
                
            recipes_by_cat[category][uname] = {
                "tier": extract_tier(uname),
                "resources": resources
            }
            
    print(f"Extracted recipes into categories: {list(recipes_by_cat.keys())}")
    
    # Save the files
    os.makedirs("data", exist_ok=True)
    for cat, rec_dict in recipes_by_cat.items():
        filename = f"data/recipes_{cat}.json"
        with open(filename, "w") as f:
            json.dump(rec_dict, f, indent=2)
        print(f"Saved {len(rec_dict)} recipes to {filename}")
        
    # Delete old recipes.json
    if os.path.exists("data/recipes.json"):
        os.remove("data/recipes.json")
        print("Deleted old data/recipes.json")

if __name__ == "__main__":
    main()
