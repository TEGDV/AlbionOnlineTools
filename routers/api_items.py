import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES
from services.crafting import calculate_crafting_profitability
from services.albion_api import fetch_market_sell_prices

router = APIRouter()

@router.get("/api/crafting/profitability")
async def get_crafting_profitability(item_unique_name: str):
    result = await calculate_crafting_profitability(item_unique_name)
    if not result:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return result

@router.get("/api/items/search")
async def search_items(search_query: Optional[str] = Query(None)):
    query_lower = search_query.strip().lower() if search_query else ""

    if not query_lower:
        return {
            "weapons": DB_WEAPONS,
            "armors": DB_ARMORS,
            "accessories": DB_ACCESSORIES,
            "consumables": DB_CONSUMABLES,
        }

    return {
        "weapons": {k: v for k, v in DB_WEAPONS.items() if query_lower in v.get("name", "").lower()},
        "armors": {k: v for k, v in DB_ARMORS.items() if query_lower in v.get("name", "").lower()},
        "accessories": {k: v for k, v in DB_ACCESSORIES.items() if query_lower in v.get("name", "").lower()},
        "consumables": {k: v for k, v in DB_CONSUMABLES.items() if query_lower in v.get("name", "").lower()},
    }

@router.get("/api/images/{unique_name}")
async def serve_image(unique_name: str):
    base_dir = "static/items"
    categories = ["weapons", "armors", "accessories", "consumables", "materials"]
    
    for category in categories:
        path = os.path.join(base_dir, category, unique_name)
        if os.path.exists(path):
            return FileResponse(path)
            
    fallback = os.path.join(base_dir, unique_name)
    if os.path.exists(fallback):
        return FileResponse(fallback)
        
    placeholder = os.path.join(base_dir, "placeholder.png")
    if os.path.exists(placeholder):
        return FileResponse(placeholder)
        
    raise HTTPException(status_code=404, detail="Image not found")

@router.get("/api/market/sell-prices")
async def get_market_sell_prices(items: str):
    return await fetch_market_sell_prices(items)
