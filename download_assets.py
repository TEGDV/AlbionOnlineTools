import os
import requests
from urllib.parse import urlparse
from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES

# Define and create the target directory
OUTPUT_DIR = os.path.join("static", "items")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Aggregate all databases
all_dbs = [DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES]


def download_assets():
    for db in all_dbs:
        for item_id, item_data in db.items():
            url = item_data.get("icon")

            # Skip if URL is missing or already converted to a local path
            if not url or not url.startswith("http"):
                continue

            # Parse the URL to drop query parameters and extract the raw filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Prevent redundant downloads if the script is interrupted and rerun
            if os.path.exists(filepath):
                continue

            print(f"Downloading: {filename}")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                else:
                    print(f"HTTP {response.status_code} failed for: {url}")
            except requests.RequestException as e:
                print(f"Network error on {url}: {e}")


if __name__ == "__main__":
    print("Initiating asset download...")
    download_assets()
    print("Download complete.")
