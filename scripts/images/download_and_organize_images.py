import json
import os
import glob
import asyncio
import aiohttp
import shutil

STATIC_DIR = "static/items"
CATEGORIES = ["weapons", "armors", "accessories", "consumables", "materials"]

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

async def download_image(session, unique_name, save_path):
    if os.path.exists(save_path):
        return True # Already exists

    url = f"https://render.albiononline.com/v1/item/{unique_name}.png?quality=4"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(save_path, 'wb') as f:
                    f.write(content)
                print(f"Downloaded: {unique_name}")
                return True
            else:
                print(f"Failed to download {unique_name} (Status: {response.status})")
                return False
    except Exception as e:
        print(f"Error downloading {unique_name}: {e}")
        return False

async def main():
    # 1. Create category folders
    for cat in CATEGORIES:
        os.makedirs(os.path.join(STATIC_DIR, cat), exist_ok=True)

    # 2. Load valid unique names
    items_data = load_json("data/items.json")
    valid_names = {item["UniqueName"] for item in items_data if "UniqueName" in item}

    # 3. Collect targets mapping {unique_name: category}
    targets = {}

    db_mappings = {
        "data/db_weapons.json": "weapons",
        "data/db_armors.json": "armors",
        "data/db_accesories.json": "accessories",
        "data/db_consumables.json": "consumables"
    }

    # Process equipment DBs
    for db_path, category in db_mappings.items():
        db_data = load_json(db_path)
        
        # Determine if db_data is a dict (by id) or list
        if isinstance(db_data, dict):
            items_list = db_data.values()
        else:
            items_list = db_data
            
        for item in items_list:
            base_id = item.get("identifier") or item.get("UniqueName")
            if not base_id: continue
            
            # The icon is already correct because we just fixed it in fix_image_locations.py
            # But we need to add the targets so they get downloaded
            
            # Check for base and @1 to @4
            for ench in ["", "@1", "@2", "@3", "@4"]:
                uname = f"{base_id}{ench}"
                if uname in valid_names:
                    targets[uname] = category
                    
        # Save the updated DB
        save_json(db_data, db_path)
        print(f"Updated paths in {db_path}")

    # Process recipes to find materials
    for recipe_file in glob.glob("data/recipes_*.json"):
        recipes = load_json(recipe_file)
        for req_name, recipe in recipes.items():
            for res in recipe.get("resources", []):
                uname = res["UniqueName"]
                # If it's not already targeted (e.g. not a weapon/armor), it's a material
                if uname not in targets and uname in valid_names:
                    targets[uname] = "materials"
                    
            # Check if the crafted item itself is missing from targets (unlikely if it's in DBs, but just in case)
            if req_name not in targets and req_name in valid_names:
                targets[req_name] = "materials" # default fallback for crafted items not in DBs

    # 4. Move existing files from static/items/ into subfolders
    for filename in os.listdir(STATIC_DIR):
        if filename.endswith(".png"):
            uname = filename[:-4]
            filepath = os.path.join(STATIC_DIR, filename)
            
            if os.path.isfile(filepath):
                category = targets.get(uname)
                if category:
                    new_path = os.path.join(STATIC_DIR, category, filename)
                    shutil.move(filepath, new_path)
                    print(f"Moved {filename} to {category}/")
                else:
                    # Move to materials as a catch-all if it exists but wasn't mapped
                    new_path = os.path.join(STATIC_DIR, "materials", filename)
                    shutil.move(filepath, new_path)
                    print(f"Moved {filename} to materials/ (fallback)")

    # 5. Download missing files asynchronously
    print(f"Total targets to ensure: {len(targets)}")
    
    # Filter only missing
    missing_targets = []
    for uname, category in targets.items():
        save_path = os.path.join(STATIC_DIR, category, f"{uname}.png")
        if not os.path.exists(save_path):
            missing_targets.append((uname, save_path))
            
    print(f"Need to download {len(missing_targets)} missing images...")
    
    # Semaphore to limit concurrent downloads to avoid overwhelming the Albion API
    sem = asyncio.Semaphore(50)
    
    async def bounded_download(session, uname, save_path):
        async with sem:
            return await download_image(session, uname, save_path)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_download(session, uname, save_path) for uname, save_path in missing_targets]
        await asyncio.gather(*tasks)
        
    print("Download and organization complete!")

if __name__ == "__main__":
    asyncio.run(main())
