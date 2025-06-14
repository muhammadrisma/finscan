from pydantic import BaseModel

class ResultLogRequest(BaseModel):
    id: str
    original_description: str

class ResultLogResponse(BaseModel):
    id: str
    original_description: str
    extracted_fish_name: str
    fish_name_english: str
    fish_name_latin: str
    flag: bool

class ResultLogDBResponse(BaseModel):
    id: str
    original_description: str
    extracted_fish_name: str
    fish_name_english: str
    fish_name_latin: str
    flag: bool 