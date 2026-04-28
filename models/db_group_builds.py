import json
import os
from pydantic import BaseModel
from typing import List, Optional, Dict
from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES
from pydantic import parse_obj_as
from models.db_builds import Build
from utils.helpers import get_base64_image

DB_FILE = "./data/db_group_builds.json"


class Role(BaseModel):
    name: str = "New Role"
    build: Build
    swaps: Optional[List[Build]] = None
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

    # Replace integer ID with the actual Item dictionary/model
    for slot, db in mapping.items():
        item_id = build_data.get(slot)
        if item_id is not None:
            # Get item from DB, default to original ID if not found
            build_data[slot] = db.get(item_id, {"id": item_id, "name": "Unknown"})
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


def load_group_builds_db() -> List[dict]:
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r") as f:
        try:
            raw_builds = json.load(f)
            return raw_builds
        except json.JSONDecodeError:
            return []


def load_group_builds_summary() -> List[dict]:
    """
    Retrieves compositions and converts the weapon icon path
    to a Base64 string for immediate rendering.
    """
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r") as f:
        try:
            raw_data = json.load(f)
            full_builds = parse_obj_as(List[GroupBuild], raw_data)

            summaries = []
            for id, build in enumerate(full_builds):
                roles_icons = []

                for role in build.roles:
                    # 1. Get the path from the object (e.g., "static/items/T8_MAIN_CURSEDSTAFF.png")
                    icon_path = DB_WEAPONS.get(role.build.weapon)["icon"]

                    # 2. Convert to Base64 using your utility
                    b64_data = get_base64_image(icon_path)

                    # 3. Format as a Data URI or fallback to original path if file is missing
                    icon_uri = (
                        f"data:image/png;base64,{b64_data}" if b64_data else icon_path
                    )
                    roles_icons.append(icon_uri)

                # 4. Map to the 'Obsidian' summary structure
                summaries.append(
                    {
                        "id": id,
                        "name": build.name,
                        "notes": build.notes,
                        "roles": roles_icons,  # List of Base64 strings
                    }
                )

            return summaries

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error generating Base64 summary: {e}")
            return []


def load_comp(target_id: int) -> Optional[Dict]:
    if not os.path.exists(DB_FILE):
        return None

    with open(DB_FILE, "r") as f:
        try:
            raw_builds = json.load(f)

            # Robust extraction: match the explicit ID key, not the list index
            target_comp = next(
                (comp for comp in raw_builds if comp.get("id") == target_id), None
            )

            if not target_comp:
                return None

            # Hydrate only the specific requested composition
            for role in target_comp.get("roles", []):
                if "build" in role and isinstance(role["build"], dict):
                    role["build"] = hydrate_build(role["build"])

                if "swaps" in role and isinstance(role["swaps"], list):
                    # 2. Dehydrate ONLY the nested 'build' dictionary
                    # dehydrate_build mutates the dictionary in place
                    if len(role["swaps"]) > 0:
                        for swap in role["swaps"]:
                            hydrate_build(swap)
                else:
                    role["swaps"] = []

            return target_comp

        except json.JSONDecodeError:
            return None


def save_group_builds_db(data: List[dict]):
    # Normalize IDs before saving to ensure they start from 0 and are sequential
    for index, item in enumerate(data):
        item["id"] = index
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
