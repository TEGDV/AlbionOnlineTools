import json
import os


def load_json_dict(filepath: str) -> dict:
    """
    Loads JSON data and maps it to a dictionary by ID,
    simultaneously encoding the icon path into a Base64 data URI.
    """
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return {item["id"]: item for item in data}

        except (json.JSONDecodeError, KeyError, Exception) as e:
            # Strict objective error reporting
            print(f"Obsidian Data Error: Failed to process {filepath}. {e}")
            return {}


# These will be loaded once when this file is first imported
DB_WEAPONS = load_json_dict("data/db_weapons.json")
DB_ARMORS = load_json_dict("data/db_armors.json")
DB_ACCESSORIES = load_json_dict("data/db_accesories.json")
DB_CONSUMABLES = load_json_dict("data/db_consumables.json")
