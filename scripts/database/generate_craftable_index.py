import json

def main():
    print("Loading recipes...")
    with open("data/recipes.json", "r") as f:
        recipes = json.load(f)
        
    base_names = set()
    for req in recipes.keys():
        # req is like T7_2H_FIRESTAFF_HELL
        parts = req.split('_', 1)
        if len(parts) == 2:
            base_names.add(parts[1])

    print(f"Found {len(base_names)} base recipe names.")
    
    print("Loading items.json...")
    with open("data/items.json", "r") as f:
        items = json.load(f)
        
    craftable_index = []
    
    for item in items:
        uname = item.get("UniqueName", "")
        if not uname: continue
        
        # Check if it matches a craftable base name
        # T7_2H_FIRESTAFF_HELL@3 -> base is 2H_FIRESTAFF_HELL
        parts = uname.split('@')[0].split('_', 1)
        if len(parts) == 2 and parts[1] in base_names:
            name = item.get("LocalizedNames", {}).get("EN-US", uname)
            craftable_index.append({
                "Index": item.get("Index"),
                "UniqueName": uname,
                "Name": name
            })
            
    with open("data/craftable_items_index.json", "w") as f:
        json.dump(craftable_index, f, indent=2)
        
    print(f"Saved {len(craftable_index)} craftable items to index.")

if __name__ == "__main__":
    main()
