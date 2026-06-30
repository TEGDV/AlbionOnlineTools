import json
import urllib.request
import os

RECIPES_FILE = "data/recipes.json"
OUTPUT_FILE = "data/enchantments_artifacts_prices.json"

def get_enchantment_ids():
    items = []
    tiers = [4, 5, 6, 7, 8]
    types = ["RUNE", "SOUL", "RELIC"]
    for t in tiers:
        for typ in types:
            items.append(f"T{t}_{typ}")
    return items

def get_artifact_ids():
    if not os.path.exists(RECIPES_FILE):
        return []
        
    with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
        
    artifacts = set()
    for reqs in recipes.values():
        for res in reqs.get('resources', []):
            name = res.get('UniqueName', '')
            if 'ARTIFACT' in name or 'ESSENCE' in name or 'RUNE' in name or 'SOUL' in name or 'RELIC' in name:
                artifacts.add(name)
    return list(artifacts)

def fetch_prices(item_ids):
    if not item_ids:
        return []
        
    # Split into chunks of 100 to avoid URL too long
    chunk_size = 100
    all_data = []
    
    for i in range(0, len(item_ids), chunk_size):
        chunk = item_ids[i:i + chunk_size]
        ids_query = ",".join(chunk)
        url = f"https://www.albion-online-data.com/api/v2/stats/prices/{ids_query}.json"
        ciudades_excluidas = {"Brecilien", "Caerleon"}
        
        req = urllib.request.Request(url, headers={"User-Agent": "AODP-Market-Client/1.0"})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                for record in data:
                    if record.get("city") not in ciudades_excluidas:
                        if record.get("sell_price_min", 0) > 0 or record.get("buy_price_max", 0) > 0:
                            all_data.append(record)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return all_data

def main():
    ench_ids = get_enchantment_ids()
    art_ids = get_artifact_ids()
    
    all_ids = list(set(ench_ids + art_ids))
    print(f"Fetching prices for {len(all_ids)} items...")
    
    prices = fetch_prices(all_ids)
    
    # Process best sell and buy prices
    results = {}
    for p in prices:
        item_id = p['item_id']
        if item_id not in results:
            results[item_id] = []
        results[item_id].append(p)
        
    final_output = []
    for item_id, locs in results.items():
        ventas_validas = [loc for loc in locs if loc["sell_price_min"] > 0]
        mejor_compra = min(ventas_validas, key=lambda x: x["sell_price_min"]) if ventas_validas else None
        
        if mejor_compra:
            final_output.append({
                "item_id": item_id,
                "city": mejor_compra["city"],
                "price": mejor_compra["sell_price_min"]
            })
            
    if not os.path.exists("data"):
        os.makedirs("data")
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(final_output)} prices to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
