import mimetypes
from urllib.parse import quote

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.file import FileOut
from app.schemas.user import ResponseModel
from app.services.auth import get_current_user
from app.services.storage import get_download_file, save_upload

router = APIRouter(tags=["storage"])

CHUNK_SIZE = 1024 * 1024


@router.post("/api/upload", response_model=ResponseModel[FileOut])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    parent_id: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = await save_upload(db, user, file, parent_id)
    return ResponseModel(data=FileOut.model_validate(record))


@router.get("/api/download/{file_id}")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        record, path = await get_download_file(db, file_id, user)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    async def file_iterator():
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    encoded_name = quote(record.name)
    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"},
    )


@router.get("/api/preview/{file_id}")
async def preview_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        record, path = await get_download_file(db, file_id, user)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    media_type = mimetypes.guess_type(record.name)[0] or "application/octet-stream"

    async def file_iterator():
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    return StreamingResponse(
        file_iterator(),
        media_type=media_type,
    )
