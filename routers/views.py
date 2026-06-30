from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from models.db_group_builds import load_group_builds_summary, load_comp, GroupBuild
from utils.processors import process_comp_icons
from services.crafting import load_json
from fastapi import HTTPException
import uuid
import logging

router = APIRouter()
templates = Jinja2Templates(directory="static/html")

@router.get("/crafting-calculator")
async def serve_crafting_calculator(request: Request):
    base_items = load_json("data/base_craftable_items.json")
    return templates.TemplateResponse(
        request=request,
        name="crafting_calculator.html",
        context={
            "page_title": "Crafting Profitability Calculator",
            "base_items": base_items
        },
    )

@router.get("/market-opportunities")
async def serve_market_opportunities(request: Request):
    meta_builds = load_json("data/meta_builds.json")
    market_data = load_json("data/market_opportunities.json")
    return templates.TemplateResponse(
        request=request,
        name="market_opportunities.html",
        context={
            "page_title": "Market Opportunities",
            "meta_builds": meta_builds,
            "market_data": market_data
        },
    )

@router.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Albion Online Tools"},
    )

@router.get("/party-compositions")
async def serve_party_compositions(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="party_compositions.html",
        context={
            "compositions": load_group_builds_summary(),
            "page_title": "Party Compositions",
        },
    )

@router.get("/party-compositions/{composition_id}")
async def serve_composition_editor(request: Request, composition_id: str):
    is_new = False
    try:
        if composition_id == "new":
            new_id = str(uuid.uuid4())
            composition_data = GroupBuild(
                id=new_id, name="New Party Composition", roles=[]
            ).model_dump()
            page_title = "New Composition"
            is_new = True
        else:
            raw_data = load_comp(composition_id)
            if not raw_data:
                raise HTTPException(status_code=404, detail="Composition not found")

            composition_data = GroupBuild.model_validate(raw_data).model_dump()
            new_id = composition_id
            page_title = composition_data["name"]

        process_comp_icons(composition_data)
        return templates.TemplateResponse(
            request=request,
            name="composition_page.html",
            context={
                "comp": composition_data,
                "id": new_id,
                "page_title": page_title,
                "is_new": is_new,
            },
        )
    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"Router Failure: {error}")
        raise HTTPException(status_code=500, detail="Internal rendering error")
