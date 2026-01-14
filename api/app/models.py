from pydantic import BaseModel
from typing import List, Optional

class AboutMember(BaseModel):
    full_name: str
    am: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class CategoryOut(BaseModel):
    id: str
    title: str
    count: int

class PoiListItem(BaseModel):
    id: str
    title: str
    lat: float
    lon: float
    image: Optional[str] = None
    short: Optional[str] = None

class PoiDetails(BaseModel):
    id: str
    category_id: str
    category_title: str
    title: str
    short: Optional[str] = None
    lat: float
    lon: float
    wikipedia_url: Optional[str] = None
    images: List[str]
    description: Optional[str] = None
