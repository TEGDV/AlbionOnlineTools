import json
import os
import asyncio
import aiohttp

STATIC_DIR = "static/items"

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

valid_names = {item["UniqueName"] for item in load_json("data/items.json") if "UniqueName" in item}
targets = {}

# We need a helper to generate T4-T8 variations of a T8 item
def generate_tier_variations(t8_name):
    if not t8_name.startswith("T8_"): return [t8_name]
    base = t8_name[3:] # e.g. "MAIN_SWORD"
    return [f"T{tier}_{base}" for tier in range(4, 9)]

db_mappings = {
    "data/db_weapons.json": "weapons",
    "data/db_armors.json": "armors",
    "data/db_accesories.json": "accessories",
    "data/db_consumables.json": "consumables"
}

# 1. Process all tiers for DB items
for db_path, category in db_mappings.items():
    db_data = load_json(db_path)
    items_list = db_data.values() if isinstance(db_data, dict) else db_data
    
    for item in items_list:
        base_id = item.get("identifier") or item.get("UniqueName")
        if not base_id: continue
        
        # Generate T4, T5, T6, T7, T8 versions
        for t_name in generate_tier_variations(base_id):
            for ench in ["", "@1", "@2", "@3", "@4"]:
                uname = f"{t_name}{ench}"
                if uname in valid_names:
                    targets[uname] = category

# 2. Add Runes, Souls, Relics, Avalonian Shards (T4 to T8)
for tier in range(4, 9):
    for mat in ["RUNE", "SOUL", "RELIC", "AVALONIAN_SHARD"]:
        uname = f"T{tier}_{mat}"
        if uname in valid_names:
            targets[uname] = "materials"

# 3. Add Enchanted Materials (T4 to T8)
base_mats = ["WOOD", "METALBAR", "LEATHER", "CLOTH", "PLANKS", "ROCK", "STONEBLOCK", "ORE", "FIBER", "HIDE"]
for tier in range(4, 9):
    for mat in base_mats:
        # Base
        uname = f"T{tier}_{mat}"
        if uname in valid_names:
            targets[uname] = "materials"
        
        # Enchanted (LEVEL1@1 to LEVEL4@4)
        for level in range(1, 5):
            uname = f"T{tier}_{mat}_LEVEL{level}@{level}"
            if uname in valid_names:
                targets[uname] = "materials"

# Check missing
missing = []
for uname, category in targets.items():
    if not os.path.exists(os.path.join(STATIC_DIR, category, f"{uname}.png")):
        missing.append((uname, category))

print(f"Total targets: {len(targets)}")
print(f"Missing files to download: {len(missing)}")

async def download_image(session, unique_name, save_path):
    url = f"https://render.albiononline.com/v1/item/{unique_name}.png?quality=4"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(save_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        return False
    return False

async def main():
    if not missing:
        print("Nothing to download!")
        return
        
    sem = asyncio.Semaphore(50)
    
    async def bounded_download(session, uname, category):
        save_path = os.path.join(STATIC_DIR, category, f"{uname}.png")
        async with sem:
            res = await download_image(session, uname, save_path)
            if res:
                print(f"Downloaded: {uname}")
            else:
                print(f"Failed: {uname}")

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_download(session, uname, category) for uname, category in missing]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

# 4. Process base_craftable_items.json to ensure no missing weapons
base_craftable = load_json("data/base_craftable_items.json")
for item in base_craftable:
    bcode = item.get("base_code")
    if not bcode: continue
    base_id = f"T8_{bcode}"
    # Generate variations
    for t_name in generate_tier_variations(base_id):
        for ench in ["", "@1", "@2", "@3", "@4"]:
            uname = f"{t_name}{ench}"
            if uname in valid_names:
                targets[uname] = "weapons" # mostly weapons/armors, we can just guess "weapons" and fix_image_locations can sort it later if needed, but the router will find it anywhere.

missing_from_base = []
for uname, category in targets.items():
    if not os.path.exists(os.path.join(STATIC_DIR, category, f"{uname}.png")):
        missing_from_base.append((uname, category))

print(f"Additional missing: {len(missing_from_base)}")
