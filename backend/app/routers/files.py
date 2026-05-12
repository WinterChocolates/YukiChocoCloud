from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.file import CreateFolderRequest, FileOut
from app.schemas.user import ResponseModel
from app.services.auth import get_current_user
from app.services.files import create_folder, delete_file, get_storage_used, list_files

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/storage")
async def storage_info(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    used = await get_storage_used(db, user)
    return {"code": 0, "message": "ok", "data": {"used": used, "total": settings.storage_limit_bytes}}


@router.get("", response_model=ResponseModel[list[FileOut]])
async def get_files(
    parent_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    files = await list_files(db, user, parent_id)
    return ResponseModel(data=[FileOut.model_validate(f) for f in files])


@router.post("", response_model=ResponseModel[FileOut])
async def create_folder_endpoint(
    body: CreateFolderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        folder = await create_folder(db, user, body.name, body.parent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ResponseModel(data=FileOut.model_validate(folder))


@router.delete("/{file_id}", response_model=ResponseModel[FileOut])
async def delete_file_endpoint(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        file = await delete_file(db, file_id, user)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    return ResponseModel(data=FileOut.model_validate(file))
