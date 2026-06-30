import io
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright

from models.db_group_builds import load_group_builds_db, save_group_builds_db, load_comp
from utils.processors import process_composition_dehydration, process_comp_icons

router = APIRouter()
templates = Jinja2Templates(directory="static/html")

@router.post("/party-compositions/{composition_uuid}", response_model=dict)
def create_composition(composition_uuid: str, composition: dict):
    database = load_group_builds_db()

    if not composition_uuid:
        composition["uuid"] = str(uuid.uuid4())

    process_composition_dehydration(composition)

    database[composition_uuid] = composition
    save_group_builds_db(database)
    return {"uuid": composition_uuid}

@router.put("/party-compositions/{composition_uuid}", response_model=dict)
def update_composition(composition_uuid: str, composition: dict):
    database = load_group_builds_db()

    if composition_uuid not in database:
        raise HTTPException(status_code=404, detail="Composition not found")

    process_composition_dehydration(composition)
    composition["uuid"] = composition_uuid
    database[composition_uuid] = composition

    save_group_builds_db(database)
    return composition

@router.delete("/party-compositions/{composition_uuid}", response_model=dict)
def delete_composition(composition_uuid: str):
    database = load_group_builds_db()

    if database.pop(composition_uuid, None) is None:
        raise HTTPException(status_code=404, detail="Composition not found")

    save_group_builds_db(database)
    return {"message": f"Composition {composition_uuid} deleted successfully"}

@router.get("/party-compositions/{composition_uuid}/export")
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
