from urllib.parse import quote

import aiofiles
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.share import CreateShareRequest, PublicShareIn, PublicShareOut, ShareOut
from app.schemas.user import ResponseModel
from app.services.auth import get_current_user
from app.services.share import access_share, create_share, delete_share, list_shares_by_file
from app.services.storage import resolve_path

router = APIRouter(tags=["shares"])


@router.post("/api/shares", response_model=ResponseModel[ShareOut])
async def create_share_endpoint(
    body: CreateShareRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        share = await create_share(db, user, body.file_id, body.password, body.expire_at)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    out = ShareOut(
        id=share.id,
        token=share.token,
        file_id=share.file_id,
        has_password=share.password is not None,
        expire_at=share.expire_at,
        created_at=share.created_at,
    )
    return ResponseModel(data=out)


@router.get("/api/files/{file_id}/shares", response_model=ResponseModel[list[ShareOut]])
async def list_shares_endpoint(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        shares = await list_shares_by_file(db, user, file_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    data = [
        ShareOut(
            id=s.id,
            token=s.token,
            file_id=s.file_id,
            has_password=s.password is not None,
            expire_at=s.expire_at,
            created_at=s.created_at,
        )
        for s in shares
    ]
    return ResponseModel(data=data)


@router.delete("/api/shares/{share_id}", response_model=ResponseModel)
async def delete_share_endpoint(
    share_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = await delete_share(db, user, share_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Share not found")
    return ResponseModel(message="Share deleted")


@router.post("/api/public/share/{token}", response_model=ResponseModel[PublicShareOut])
async def access_share_endpoint(
    token: str,
    body: PublicShareIn = PublicShareIn(),
    db: AsyncSession = Depends(get_db),
):
    try:
        file = await access_share(db, token, body.password)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Share not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return ResponseModel(data=PublicShareOut(file_name=file.name, file_size=file.size, is_dir=file.is_dir))


CHUNK_SIZE = 1024 * 1024


@router.post("/api/public/share/{token}/download")
async def download_share_endpoint(
    token: str,
    body: PublicShareIn = PublicShareIn(),
    db: AsyncSession = Depends(get_db),
):
    try:
        file = await access_share(db, token, body.password)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Share not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if file.is_dir:
        raise HTTPException(status_code=400, detail="Cannot download folder")

    path = resolve_path(file.storage_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    async def file_iterator():
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    encoded_name = quote(file.name)
    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"},
    )
