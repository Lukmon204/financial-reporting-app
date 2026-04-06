from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str
    status: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    base_id: Optional[int] = None

class User    id: int
    username: str
    email: str
    full_name: str
    role: str
    status: str
    base_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    status: str
    base_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True