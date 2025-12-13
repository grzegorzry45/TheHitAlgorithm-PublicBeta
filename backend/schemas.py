from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

class PresetBase(BaseModel):
    name: str
    profile: Dict[str, Any]

class PresetCreate(PresetBase):
    pass

class Preset(PresetBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    presets: List[Preset] = []

    class Config:
        from_attributes = True # Changed from orm_mode = True for Pydantic v2.0+

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
