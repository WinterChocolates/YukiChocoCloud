from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateShareRequest(BaseModel):
    file_id: int
    password: Optional[str] = Field(None, max_length=128)
    expire_at: Optional[datetime] = None


class ShareOut(BaseModel):
    id: int
    token: str
    file_id: int
    has_password: bool
    expire_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicShareIn(BaseModel):
    password: Optional[str] = None


class PublicShareOut(BaseModel):
    file_name: str
    file_size: int
    is_dir: bool

    model_config = {"from_attributes": True}
