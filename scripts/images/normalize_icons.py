import json
import os
import glob
import urllib.parse

def main():
    print("Loading items.json...")
    with open("data/items.json", "r") as f:
        items = json.load(f)
    
    # Create mapping: "Elder's Arclight Blasters" -> "T8_2H_DUALCROSSBOW_CRYSTAL"
    # Note: We need to handle names without prefixes as well, if any, but since the
    # files might have the exact LocalizedName in English, we map exactly that.
    name_to_unique = {}
    for item in items:
        uname = item.get("UniqueName", "")
        # Filter out enchantments for base mapping, or just map everything!
        if "@" in uname:
            continue
            
        localized_names = item.get("LocalizedNames")
        if localized_names:
            local_name = localized_names.get("EN-US", "")
            if local_name:
                name_to_unique[local_name] = uname
            
    print(f"Loaded {len(name_to_unique)} name mappings.")

    # 1. Rename files in static/items/
    print("Normalizing static/items/ ...")
    renamed_count = 0
    for file_path in glob.glob("static/items/*.png"):
        basename = os.path.basename(file_path)
        # e.g., "Elder's Arclight Blasters@0.png"
        name_no_ext = basename[:-4]
        
        # Split by @ if exists
        parts = name_no_ext.split("@")
        local_name = parts[0]
        enchant = parts[1] if len(parts) > 1 else ""
        
        # If it's already uppercase snake case, skip
        if local_name.isupper() and "_" in local_name:
            continue
            
        if local_name in name_to_unique:
            uname = name_to_unique[local_name]
            new_name = f"{uname}@{enchant}.png" if enchant else f"{uname}.png"
            new_path = os.path.join("static/items", new_name)
            os.rename(file_path, new_path)
            renamed_count += 1
            print(f"Renamed: {basename} -> {new_name}")
        else:
            # Maybe it's URL encoded?
            decoded = urllib.parse.unquote(local_name)
            if decoded in name_to_unique:
                uname = name_to_unique[decoded]
                new_name = f"{uname}@{enchant}.png" if enchant else f"{uname}.png"
                new_path = os.path.join("static/items", new_name)
                os.rename(file_path, new_path)
                renamed_count += 1
                print(f"Renamed: {basename} -> {new_name}")

    print(f"Total renamed images: {renamed_count}")
    
    # 2. Update JSON files
    def fix_json(file_path):
        print(f"Normalizing {file_path} ...")
        with open(file_path, "r") as f:
            data = json.load(f)
            
        updated = 0
        for entry in data:
            icon = entry.get("icon", "")
            if not icon: continue
            
            # Extract basename: /static/items/Elder's Arclight Blasters@0.png
            basename = icon.split("/")[-1]
            if not basename.endswith(".png"): continue
            name_no_ext = basename[:-4]
            
            parts = name_no_ext.split("@")
            local_name = urllib.parse.unquote(parts[0])
            enchant = parts[1] if len(parts) > 1 else ""
            
            if local_name.isupper() and "_" in local_name:
                continue
                
            if local_name in name_to_unique:
                uname = name_to_unique[local_name]
                new_name = f"{uname}@{enchant}.png" if enchant else f"{uname}.png"
                entry["icon"] = icon.replace(basename, new_name)
                updated += 1
                
        if updated > 0:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Updated {updated} entries in {file_path}.")
        else:
            print(f"No updates needed for {file_path}.")

    fix_json("data/weapons.json")
    fix_json("data/db_weapons.json")
    fix_json("data/db_armors.json")
    fix_json("data/db_accesories.json")
    fix_json("data/db_consumables.json")

if __name__ == "__main__":
    main()
