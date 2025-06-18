from pydantic import BaseModel

class ResultLogRequest(BaseModel):
    original_description: str
    no_peb: str
    no_seri: str

class ResultLogResponse(BaseModel):
    id: int
    no_peb: str
    no_seri: str
    original_description: str
    extracted_fish_name: str
    fish_name_english: str
    fish_name_latin: str
    flag: bool
    from_cache: bool = False

class ResultLogDBResponse(BaseModel):
    id: int
    no_peb: str
    no_seri: str
    original_description: str
    extracted_fish_name: str
    fish_name_english: str
    fish_name_latin: str
    flag: bool
    from_cache: bool = False 