from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[int] = None


class FileOut(BaseModel):
    id: int
    name: str
    is_dir: bool
    size: int
    created_at: datetime

    model_config = {"from_attributes": True}
