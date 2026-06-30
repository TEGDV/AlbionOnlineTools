import json

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

raw = load_json("data/raw_items.json")

item_values = {}

def traverse(obj):
    if isinstance(obj, dict):
        if "@uniquename" in obj and "@itemvalue" in obj:
            item_values[obj["@uniquename"]] = float(obj["@itemvalue"])
        for k, v in obj.items():
            traverse(v)
    elif isinstance(obj, list):
        for item in obj:
            traverse(item)

traverse(raw)

with open("data/item_values.json", "w") as f:
    json.dump(item_values, f, indent=2)

print(f"Extracted {len(item_values)} item values.")
