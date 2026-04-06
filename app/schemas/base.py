from pydantic import BaseModel
from datetime import datetime

class BaseInfoBase(BaseModel):
    name: str
    location: str

class BaseInfoCreate(BaseInfoBase):
    pass

class BaseInfoUpdate(BaseModel):
    name: str
    location: str

class BaseInfoResponse(BaseModel):
    id: int
    name: str
    location: str
    created_at: datetime
    
    class Config:
        from_attributes = True