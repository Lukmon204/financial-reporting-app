from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str