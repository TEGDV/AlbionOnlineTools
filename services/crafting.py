import os
import json
import glob
from services.albion_api import fetch_prices

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_all_recipes():
    recipes = {}
    for filepath in glob.glob("data/recipes_*.json"):
        cat_recipes = load_json(filepath)
        if isinstance(cat_recipes, dict):
            recipes.update(cat_recipes)
    return recipes

ITEM_VALUES = load_json("data/item_values.json")

def get_enchantment_reqs(tier, enchant_level, base_name=""):
    reqs = []
    
    count = 384
    if "_MAIN_" in base_name:
        count = 288
    elif any(k in base_name for k in ["_OFF_", "_HEAD_", "_SHOES_", "CAPE", "_BAG"]):
        count = 96
    elif "_ARMOR_" in base_name:
        count = 192
    elif "_2H_" in base_name:
        count = 384
        
    names = ["RUNE", "SOUL", "RELIC", "SHARD_AVALON"]
    for i in range(enchant_level):
        if i < len(names):
            reqs.append({"name": f"T{tier}_{names[i]}", "count": count, "value": 0})
    return reqs

async def calculate_crafting_profitability(item_unique_name: str):
    recipes = load_all_recipes()
    
    parts = item_unique_name.split('@')
    base_name = parts[0]
    enchant_level = int(parts[1]) if len(parts) > 1 else 0
    
    if base_name not in recipes:
        return None
        
    recipe = recipes[base_name]
    tier = recipe['tier']
    
    direct_reqs = []
    for res in recipe['resources']:
        res_name = res['UniqueName']
        if "WOOD" in res_name or "METAL" in res_name or "LEATHER" in res_name or "CLOTH" in res_name or "PLANKS" in res_name:
            if enchant_level > 0:
                res_name += f"_LEVEL{enchant_level}@{enchant_level}"
        elif res_name.endswith("_CAPE"):
            if enchant_level > 0:
                res_name += f"@{enchant_level}"
        direct_reqs.append({"name": res_name, "count": res['count'], "value": 0})
        
    enchant_reqs_base = []
    for res in recipe['resources']:
        enchant_reqs_base.append({"name": res['UniqueName'], "count": res['count'], "value": 0})
        
    enchant_materials = get_enchantment_reqs(tier, enchant_level, base_name)

    all_item_ids = [item_unique_name]
    if enchant_level > 0:
        all_item_ids.append(base_name)
        
    for req in direct_reqs:
        all_item_ids.append(req["name"])
    for req in enchant_reqs_base:
        all_item_ids.append(req["name"])
    for req in enchant_materials:
        all_item_ids.append(req["name"])
        
    prices = await fetch_prices(all_item_ids)
    
    direct_craft_cost = 0
    for req in direct_reqs:
        req["value"] = prices.get(req["name"], 0)
        direct_craft_cost += req["value"] * req["count"]
        
    enchanting_route_base_cost = 0
    for req in enchant_reqs_base:
        req["value"] = prices.get(req["name"], 0)
        enchanting_route_base_cost += req["value"] * req["count"]
        
    enchanting_route_cost = 0
    if enchant_level > 0:
        enchant_mats_cost = 0
        for req in enchant_materials:
            req["value"] = prices.get(req["name"], 0)
            enchant_mats_cost += req["value"] * req["count"]
            
        base_item_price = prices.get(base_name, 0)
        if base_item_price > 0 and base_item_price < enchanting_route_base_cost:
            enchanting_route_cost = base_item_price + enchant_mats_cost
        else:
            enchanting_route_cost = enchanting_route_base_cost + enchant_mats_cost
    else:
        enchanting_route_cost = enchanting_route_base_cost

    final_item_price = prices.get(item_unique_name, 0)
    
    recommended = "direct"
    if enchant_level > 0 and enchanting_route_cost > 0 and enchanting_route_cost < direct_craft_cost:
        recommended = "enchant"

    item_value = 0
    for req in direct_reqs:
        base_req_name = req["name"].split("@")[0]
        item_value += ITEM_VALUES.get(base_req_name, 0) * req["count"]

    return {
        "item_id": item_unique_name,
        "item_value": item_value,
        "tier": tier,
        "enchantment": enchant_level,
        "final_item_price": final_item_price,
        "direct_route": direct_reqs,
        "enchanting_route_base": enchant_reqs_base,
        "enchanting_route_mats": enchant_materials,
        "direct_craft_cost": direct_craft_cost,
        "enchanting_route_cost": enchanting_route_cost,
        "recommended": recommended,
    }
