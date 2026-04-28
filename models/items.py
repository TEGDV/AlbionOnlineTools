from pydantic import BaseModel
from typing import Optional, List
from models.spells import Spell


class ItemCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None


class ItemSubcategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None


class Item(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    tier: Optional[str] = None
    item_power: Optional[int] = None
    identifier: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[ItemCategory] = None
    subcategory: Optional[ItemSubcategory] = None


class Weapon(Item):
    spells: Optional[List[Spell]] = None


class Consumable(Item):
    info: Optional[str] = None


class Armor(Item):
    spells: Optional[List[Spell]] = None


class Accesory(Item):
    spells: Optional[List[Spell]] = None
