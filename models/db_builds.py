from pydantic import BaseModel
from models.items import Weapon, Armor, Consumable, Accesory
from typing import Optional, Union

DB_FILE = "./data/db_builds.json"


class Build(BaseModel):
    # All fields are now optional and default to None
    name: Optional[str] = None

    # Union types allow for either raw Integer IDs or full Item objects
    weapon: Optional[Union[int, Weapon]] = None
    off_hand: Optional[Union[int, Weapon]] = None

    head: Optional[Union[int, Armor]] = None
    chest: Optional[Union[int, Armor]] = None
    feet: Optional[Union[int, Armor]] = None
    cape: Optional[Union[int, Accesory]] = None

    food: Optional[Union[int, Consumable]] = None
    potion: Optional[Union[int, Consumable]] = None

    bag: Optional[int] = None
