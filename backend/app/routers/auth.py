from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    LoginRequest,
    RegisterRequest,
    ResponseModel,
    TokenData,
    UserOut,
)
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_username,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=ResponseModel[UserOut])
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = await create_user(db, body.username, body.password)
    return ResponseModel(data=UserOut.model_validate(user))


@router.post("/login", response_model=ResponseModel[TokenData])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return ResponseModel(data=TokenData(access_token=token))
