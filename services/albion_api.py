import os
import json
import time
import aiohttp
from datetime import datetime, timedelta
import urllib.parse

PRICE_CACHE_FILE = "data/price_cache.json"

def load_price_cache():
    if os.path.exists(PRICE_CACHE_FILE):
        try:
            with open(PRICE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_price_cache():
    try:
        with open(PRICE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(PRICE_CACHE, f)
    except:
        pass

PRICE_CACHE = load_price_cache()
CACHE_EXPIRY = 3600  # 1 hour

async def fetch_prices(item_ids: list[str]) -> dict:
    if not item_ids:
        return {}
        
    now = time.time()
    prices = {}
    missing_ids = []
    
    for item_id in set(item_ids):
        if item_id in PRICE_CACHE and now - PRICE_CACHE[item_id]["timestamp"] < CACHE_EXPIRY:
            prices[item_id] = PRICE_CACHE[item_id]["price"]
        else:
            missing_ids.append(item_id)
            
    if missing_ids:
        ids_query = ",".join(missing_ids)
        url = f"https://www.albion-online-data.com/api/v2/stats/prices/{ids_query}.json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp_prices = {}
                        
                        for item_id in missing_ids:
                            temp_prices[item_id] = []
                            
                        excluded_cities = {"Brecilien", "Caerleon"}
                        for record in data:
                            city = record.get("city")
                            if city in excluded_cities:
                                continue
                            
                            item_id = record.get("item_id")
                            sell_price = record.get("sell_price_min", 0)
                            if sell_price > 0 and item_id in temp_prices:
                                temp_prices[item_id].append(sell_price)
                        
                        for item_id in missing_ids:
                            best_price = min(temp_prices[item_id]) if temp_prices[item_id] else 0
                            prices[item_id] = best_price
                            PRICE_CACHE[item_id] = {"price": best_price, "timestamp": now}
                        save_price_cache()
        except Exception as e:
            print(f"Error fetching prices: {e}")
            for item_id in missing_ids:
                prices[item_id] = 0
                
    return prices

async def fetch_market_sell_prices(items: str) -> dict:
    if not items:
        return {}

    now = datetime.now()
    start_date = (now - timedelta(days=7)).strftime("%m-%d-%Y")
    end_date = now.strftime("%m-%d-%Y")
    
    ids_query = urllib.parse.quote(items.strip())
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{ids_query}.json?date={start_date}&end_date={end_date}&time-scale=24"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "AODP-Avg-Client/1.3"}
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {}
                data = await response.json()
                
                resultados_crudos = {}
                
                for record in data:
                    location = record.get("location", "Desconocida")
                    item_id = record.get("item_id", "Desconocido")
                    puntos = record.get("data", [])
                    
                    precios_validos = [p["avg_price"] for p in puntos if p.get("avg_price", 0) > 0]
                    
                    if precios_validos:
                        promedio = int(sum(precios_validos) / len(precios_validos))
                        
                        if item_id not in resultados_crudos:
                            resultados_crudos[item_id] = {}
                        resultados_crudos[item_id][location] = promedio
                
                final_results = {}
                for item_id, locs in resultados_crudos.items():
                    if not locs:
                        continue
                    mejor_ciudad = max(locs, key=locs.get)
                    mejor_precio = locs[mejor_ciudad]
                    final_results[item_id] = {
                        "city": mejor_ciudad,
                        "price": mejor_precio
                    }
                
                return final_results
    except Exception as e:
        print(f"Error fetching sell prices: {e}")
        return {}
