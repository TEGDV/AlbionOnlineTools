import io
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from playwright.async_api import async_playwright

from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES
from models.db_group_builds import (
    GroupBuild,
    load_comp,
    load_group_builds_db,
    load_group_builds_summary,
    save_group_builds_db,
)
from utils.processors import process_comp_icons, process_composition_dehydration

# --- System Configuration ---


class PngLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return ".png" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(PngLogFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend())
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="static/html")

# --- Core Item API ---


@app.get("/api/items/search")
@cache(expire=3600)
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
        "weapons": {
            k: v
            for k, v in DB_WEAPONS.items()
            if query_lower in v.get("name", "").lower()
        },
        "armors": {
            k: v
            for k, v in DB_ARMORS.items()
            if query_lower in v.get("name", "").lower()
        },
        "accessories": {
            k: v
            for k, v in DB_ACCESSORIES.items()
            if query_lower in v.get("name", "").lower()
        },
        "consumables": {
            k: v
            for k, v in DB_CONSUMABLES.items()
            if query_lower in v.get("name", "").lower()
        },
    }


# --- View Routes ---


@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "page_title": "Albion Online Tools"}
    )


@app.get("/party-compositions")
async def serve_party_compositions(request: Request):
    return templates.TemplateResponse(
        "party_compositions.html",
        {
            "request": request,
            "compositions": load_group_builds_summary(),
            "page_title": "Party Compositions",
        },
    )


@app.get("/party-compositions/{composition_id}", response_class=HTMLResponse)
async def serve_composition_editor(request: Request, composition_id: str):
    try:
        if composition_id == "new":
            new_id = str(uuid.uuid4())
            composition_data = GroupBuild(
                id=new_id, name="New Party Composition", roles=[]
            ).model_dump()
            page_title = "New Composition"
        else:
            raw_data = load_comp(composition_id)
            if not raw_data:
                raise HTTPException(status_code=404, detail="Composition not found")

            composition_data = GroupBuild.model_validate(raw_data).model_dump()
            new_id = composition_id
            page_title = composition_data["name"]

        process_comp_icons(composition_data)
        return templates.TemplateResponse(
            "composition_page.html",
            {
                "request": request,
                "comp": composition_data,
                "id": new_id,
                "page_title": page_title,
            },
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Router Failure: {error}")
        raise HTTPException(status_code=500, detail="Internal rendering error")


# --- Composition Management API ---


@app.post("/party-compositions", response_model=dict)
def create_composition(composition: dict):
    database = load_group_builds_db()

    if "uuid" not in composition:
        composition["uuid"] = str(uuid.uuid4())

    composition_uuid = composition["uuid"]
    process_composition_dehydration(composition)

    database[composition_uuid] = composition
    save_group_builds_db(database)
    return composition_uuid


@app.put("/party-compositions/{composition_uuid}", response_model=dict)
def update_composition(composition_uuid: str, composition: dict):
    database = load_group_builds_db()

    if composition_uuid not in database:
        raise HTTPException(status_code=404, detail="Composition not found")

    process_composition_dehydration(composition)
    composition["uuid"] = composition_uuid
    database[composition_uuid] = composition

    save_group_builds_db(database)
    return composition


@app.delete("/party-compositions/{composition_uuid}", response_model=dict)
def delete_composition(composition_uuid: str):
    database = load_group_builds_db()

    if database.pop(composition_uuid, None) is None:
        raise HTTPException(status_code=404, detail="Composition not found")

    save_group_builds_db(database)
    return {"message": f"Composition {composition_uuid} deleted successfully"}


# --- Export Services ---


@app.get("/party-compositions/{composition_uuid}/export")
async def export_composition_as_png(composition_uuid: str):
    composition_data = load_comp(composition_uuid)
    process_comp_icons(composition_data)

    template = templates.get_template("composition_export_layout.html")
    html_content = template.render(comp=composition_data)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, device_scale_factor=2
        )
        page = await context.new_page()

        await page.set_content(html_content, wait_until="networkidle")
        image_bytes = await page.locator("#export-canvas").screenshot(type="png")
        await browser.close()

    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
