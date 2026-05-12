from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
