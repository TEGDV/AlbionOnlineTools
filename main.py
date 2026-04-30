from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import Query
import io
import uuid
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from fastapi import Request
from utils.processors import process_comp_icons, process_composition_dehydration
from typing import Optional
from models.db_group_builds import GroupBuild
from models.db_group_builds import (
    load_group_builds_db,
    load_comp,
    save_group_builds_db,
    load_group_builds_summary,
)
from models.database import DB_WEAPONS, DB_ARMORS, DB_ACCESSORIES, DB_CONSUMABLES
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from contextlib import asynccontextmanager
import logging
from fastapi.responses import HTMLResponse


class PNGLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Returns False to suppress logs containing .png
        return ".png" not in record.getMessage()


# Apply the filter to the uvicorn access logger
logging.getLogger("uvicorn.access").addFilter(PNGLogFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the cache on startup
    FastAPICache.init(InMemoryBackend())
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="static/components/templates")


@app.get("/api/")
def get_api():
    return {}


@app.get("/api/items/search")
@cache(expire=3600)  # Cache results for 1 hour
async def search_items(q: Optional[str] = Query(None)):
    query_lower = q.strip().lower() if q else ""

    # Return full DB if no query is provided
    if not query_lower:
        return {
            "weapons": DB_WEAPONS,
            "armors": DB_ARMORS,
            "accessories": DB_ACCESSORIES,
            "consumables": DB_CONSUMABLES,
        }

    # Filtered logic
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


@app.get("/")
async def serve_home(request: Request):
    """
    Serves the home dashboard with a dynamic title.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "page_title": "Albion Online Tools"}
    )


@app.get("/default")
async def serve_default_feature(request: Request):
    """
    Serves the home dashboard with a dynamic title.
    """
    return templates.TemplateResponse(
        "tool_layout.html", {"request": request, "page_title": "Default"}
    )


@app.get("/party-compositions")
async def serve_party_compositions(request: Request):
    group_builds_summary = load_group_builds_summary()

    # Return a TemplateResponse, passing the 'request' and your data
    return templates.TemplateResponse(
        "party_compositions.html",
        {
            "request": request,
            "comps": group_builds_summary,
            "page_title": "Party Compositions",
            "description": "Archived Party Composition Database",
        },
    )


@app.get("/party-compositions/{comp_id}", response_class=HTMLResponse)
async def serve_composition(request: Request, comp_id: str):
    try:
        if comp_id == "new":
            # Factory Branch: Initialize fresh state
            final_id = str(uuid.uuid4())
            composition = GroupBuild(
                id=final_id, name="New Party Composition", roles=[]
            )
            page_title = "New Composition"
        else:
            # Retrieval Branch: Load from persistent storage
            composition_data = load_comp(comp_id)
            if not composition_data:
                raise HTTPException(status_code=404, detail="Composition not found")

            # Strict model validation
            composition = GroupBuild.model_validate(composition_data)
            final_id = comp_id
            page_title = composition.name

        # Common Processing Path
        composition_data_dict = composition.model_dump()
        process_comp_icons(composition_data_dict)

        return templates.TemplateResponse(
            "composition_page.html",
            {
                "request": request,
                "comp": composition_data_dict,
                "id": final_id,
                "page_title": page_title,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        # Strict objective error logging
        print(f"Composition Router Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error processing composition"
        )


@app.post("/party-compositions", response_model=dict)
def create_party_composition(comp: dict):
    db = load_group_builds_db()
    process_composition_dehydration(comp)

    if "uuid" not in comp:
        comp["uuid"] = str(uuid.uuid4())

    db.append(comp)
    save_group_builds_db(db)
    return comp


@app.put("/party-compositions/{comp_uuid}", response_model=dict)
def update_party_composition(comp_uuid: str, comp: dict):
    db = load_group_builds_db()
    process_composition_dehydration(comp)

    for index, existing_comp in enumerate(db):
        if existing_comp.get("uuid") == comp_uuid:
            comp["uuid"] = comp_uuid  # Maintain identity
            db[index] = comp
            save_group_builds_db(db)
            return comp

    raise HTTPException(status_code=404, detail="Composition not found")


@app.delete("/party-compositions/{comp_uuid}", response_model=dict)
def delete_party_composition(comp_uuid: str):
    db = load_group_builds_db()
    initial_len = len(db)

    # Filter by uuid string
    db = [c for c in db if c.get("uuid") != comp_uuid]

    if len(db) == initial_len:
        raise HTTPException(status_code=404, detail="Composition not found")

    save_group_builds_db(db)
    return {"message": f"Composition {comp_uuid} deleted successfully"}


@app.get("/party-compositions/{comp_uuid}/export")
async def export_composition(comp_uuid: str):
    comp_data = load_comp(comp_uuid)
    process_comp_icons(comp_data)

    # Render
    template = templates.get_template("composition_export_layout.html")
    html_content = template.render(comp=comp_data)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # device_scale_factor: 2 is like Retina, 3 is extremely high detail.
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, device_scale_factor=2
        )
        page = await context.new_page()
        await page.set_content(html_content, wait_until="networkidle")

        element = page.locator("#export-canvas")
        image_bytes = await element.screenshot(type="png")
        await browser.close()

    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")


# LEGACY ==============


# Builds
if __name__ == "__main__":
    # "main:app" refers to: [filename]:[FastAPI instance name]
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
