from pydantic import BaseModel
from typing import List

class TopFishItem(BaseModel):
    fish_name_english: str
    fish_name_latin: str
    count: int

class TopFishResponse(BaseModel):
    items: List[TopFishItem] 