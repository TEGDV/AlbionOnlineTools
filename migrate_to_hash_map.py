import json
import os
import shutil
from datetime import datetime

# Configuration
DB_PATH = "data/db_group_builds.json"
BACKUP_DIR = "data/backups"


def migrate_to_hashmap():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    # 1. Create a backup before proceeding
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"group_builds_backup_{timestamp}.json")
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created at: {backup_path}")

    # 2. Load and Transform
    with open(DB_PATH, "r") as f:
        data = json.load(f)

    if isinstance(data, dict):
        print("Database is already in Hash Map format. Migration skipped.")
        return

    if not isinstance(data, list):
        print("Error: Unknown database format.")
        return

    # Convert Array -> Hash Map using 'uuid' as key
    hash_map_db = {}
    for entry in data:
        entry_id = entry.get("uuid")
        if entry_id:
            hash_map_db[str(entry_id)] = entry
        else:
            print(
                f"Warning: Skipping entry with missing UUID: {entry.get('name', 'Unknown')}"
            )

    # 3. Save the new structure
    with open(DB_PATH, "w") as f:
        json.dump(hash_map_db, f, indent=4)

    print(f"Successfully migrated {len(hash_map_db)} entries to Hash Map format.")


if __name__ == "__main__":
    migrate_to_hashmap()
