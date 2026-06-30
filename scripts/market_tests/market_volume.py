import json
import urllib.request
import os
from datetime import datetime, timedelta

def get_market_volume(item_ids):
    if not item_ids:
        return []
        
    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime("%m-%d-%Y")
    end_date = now.strftime("%m-%d-%Y")
    
    chunk_size = 50
    all_data = []
    ciudades_excluidas = {"Brecilien", "Caerleon"}
    
    for i in range(0, len(item_ids), chunk_size):
        chunk = item_ids[i:i + chunk_size]
        ids_query = ",".join(chunk)
        
        url = f"https://www.albion-online-data.com/api/v2/stats/history/{ids_query}.json?date={start_date}&end_date={end_date}&time-scale=24"
        
        req = urllib.request.Request(url, headers={"User-Agent": "AODP-Avg-Client/1.3"})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                for record in data:
                    location = record.get("location", "Desconocida")
                    if location in ciudades_excluidas:
                        continue
                        
                    item_id = record.get("item_id")
                    puntos = record.get("data", [])
                    
                    total_volume = sum([p.get("item_count", 0) for p in puntos])
                    
                    if total_volume > 0:
                        all_data.append({
                            "item_id": item_id,
                            "location": location,
                            "volume": total_volume
                        })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    # Group by item and sort by volume
    grouped = {}
    for entry in all_data:
        item = entry['item_id']
        if item not in grouped:
            grouped[item] = []
        grouped[item].append(entry)
        
    results = []
    for item, locs in grouped.items():
        best_loc = max(locs, key=lambda x: x['volume'])
        results.append({
            "item_id": item,
            "best_city": best_loc['location'],
            "highest_volume": best_loc['volume']
        })
        
    return results

def main():
    # If meta builds exists, read it
    meta_file = "data/meta_builds.json"
    item_ids = []
    
    if os.path.exists(meta_file):
        with open(meta_file, 'r', encoding='utf-8') as f:
            builds = json.load(f)
            # We'll map standard names to IDs in a real scenario
            # For now, we'll try to find some standard items
            # E.g. "Bloodletter" -> "T8_MAIN_DAGGER_MAGIC" (example)
            # This is a simplification for the scope.
            pass
            
    # As a test, use some common items
    item_ids = ["T7_MAIN_DAGGER_MAGIC", "T7_2H_SWORD", "T7_MAIN_CROSSBOW"]
    
    print(f"Fetching market volume for {len(item_ids)} items...")
    results = get_market_volume(item_ids)
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    output = "data/market_opportunities.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"Saved market opportunities to {output}")

if __name__ == "__main__":
    main()
