from pydantic import BaseModel
from typing import List, Optional


class SpellAttribute(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None


class Spell(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slot: Optional[str] = None
    preview: Optional[str] = None
    icon: Optional[str] = None
    attributes: Optional[List[SpellAttribute]] = None
    description: Optional[str] = None
    description_html: Optional[str] = None


class SpellSlotGroup(BaseModel):
    slot: Optional[str] = None
    spells: Optional[List[Spell]] = None
