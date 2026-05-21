import json
import os
import uuid
import copy
from pydantic import BaseModel, parse_obj_as
from typing import List, Optional, Dict
from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES
from models.db_builds import Build
from utils.helpers import get_base64_image

DB_FILE = "./data/db_group_builds.json"
_DB_CACHE = None


class Role(BaseModel):
    name: str = "New Role"
    build: Build
    swaps: Optional[List[Build]] = []
    notes: str = "Default Notes"


class GroupBuild(BaseModel):
    name: str = "New Composition"
    roles: List[Role]
    notes: str = "Description..."


def hydrate_build(build_data: dict) -> dict:
    """Helper to replace IDs with actual item objects."""
    # Mapping slot keys to their respective global dictionaries
    mapping = {
        "weapon": DB_WEAPONS,
        "off_hand": DB_WEAPONS,  # Off-hands often share weapon DB or have their own
        "head": DB_ARMORS,
        "chest": DB_ARMORS,
        "feet": DB_ARMORS,
        "cape": DB_ACCESSORIES,
        "bag": DB_ACCESSORIES,
        "food": DB_CONSUMABLES,
        "potion": DB_CONSUMABLES,
    }

    # Replace integer ID with a copy of the actual Item dictionary
    for slot, db in mapping.items():
        item_id = build_data.get(slot)
        if item_id is not None:
            # Get item from DB, default to original ID if not found
            item_raw = db.get(item_id)
            if item_raw:
                build_data[slot] = item_raw.copy()  # Prevent mutating global DB
            else:
                build_data[slot] = {"id": item_id, "name": "Unknown"}
        else:
            build_data[slot] = None  # Handle the "None" case
    return build_data


def dehydrate_build(build_data: dict) -> dict:
    """Helper to replace actual item objects with their integer IDs."""
    slots = [
        "weapon",
        "off_hand",
        "head",
        "chest",
        "feet",
        "cape",
        "bag",
        "food",
        "potion",
    ]

    for slot in slots:
        # get() prevents KeyErrors if the slot is entirely missing from the payload
        item_obj = build_data.get(slot)

        if isinstance(item_obj, dict) and "id" in item_obj:
            build_data[slot] = item_obj["id"]
        # If item_obj is None, or already an integer, no mutation is required.

    return build_data


def load_group_builds_db() -> Dict[str, dict]:
    """Loads the entire database as a HashMap, using in-memory cache to avoid disk reads."""
    global _DB_CACHE
    if _DB_CACHE is not None:
        return _DB_CACHE

    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        save_group_builds_db({})
        return {}

    with open(DB_FILE, "r") as f:
        try:
            _DB_CACHE = json.load(f)
            return _DB_CACHE
        except json.JSONDecodeError:
            _DB_CACHE = {}
            return _DB_CACHE


def load_group_builds_summary() -> List[dict]:
    """
    Retrieves compositions and converts the weapon icon path
    to a Base64 string for immediate rendering.
    """
    db_compositions = load_group_builds_db()
    if not db_compositions:
        return []

    try:
        compositions = parse_obj_as(Dict[str, GroupBuild], db_compositions)

        summaries = []
        for uuid_str, composition in compositions.items():
            role_icons = []

            for role in composition.roles:
                weapon = DB_WEAPONS.get(role.build.weapon, None)
                if weapon:
                    icon_path = weapon["icon"]
                    # If it's already a base64 Data URI, use it directly
                    if icon_path.startswith("data:"):
                        icon_uri = icon_path
                    else:
                        # Otherwise convert the local asset file
                        filename = icon_path.split("/")[-1]
                        local_path = os.path.join("static", "items", filename)
                        b64_data = get_base64_image(local_path)
                        icon_uri = (
                            f"data:image/png;base64,{b64_data}"
                            if b64_data
                            else icon_path
                        )
                    role_icons.append(icon_uri)

            # Map to the 'Obsidian' summary structure
            summaries.append(
                {
                    "id": uuid_str,  # Now returns the UUID string
                    "name": composition.name,
                    "notes": composition.notes,
                    "roles": role_icons,  # List of Base64 strings
                }
            )

        return summaries

    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating Base64 summary: {e}")
        return []


def load_comp(target_uuid: str) -> Optional[Dict]:
    """O(1) retrieval using UUID as the key."""
    db = load_group_builds_db()

    # Direct lookup replaces sequential search
    raw_comp = db.get(target_uuid)

    if not raw_comp:
        return None

    # Deep copy to prevent hydration mutations from leaking into the in-memory cache
    target_comp = copy.deepcopy(raw_comp)

    # Recursive hydration logic
    for role in target_comp.get("roles", []):
        if "build" in role and isinstance(role["build"], dict):
            role["build"] = hydrate_build(role["build"])

        if "swaps" in role and isinstance(role["swaps"], list):
            for swap in role["swaps"]:
                hydrate_build(swap)

    return target_comp


def save_group_builds_db(data: Dict[str, dict]):
    """Persists the HashMap to the JSON file and updates in-memory cache."""
    global _DB_CACHE
    _DB_CACHE = data
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
