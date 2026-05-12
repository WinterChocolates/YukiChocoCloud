import os
from datetime import datetime
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.file import File
from app.models.user import User
from app.services.files import get_file_by_id

CHUNK_SIZE = 1024 * 1024


def build_storage_path(user_id: int, filename: str) -> tuple[str, str]:
    now = datetime.utcnow()
    relative = os.path.join(str(user_id), f"{now:%Y}", f"{now:%m}", filename)
    full = os.path.join(settings.UPLOAD_DIR, relative)
    return relative, full


async def save_upload(db: AsyncSession, user: User, file: UploadFile, parent_id: int | None) -> File:
    relative, full = build_storage_path(user.id, file.filename)
    os.makedirs(os.path.dirname(full), exist_ok=True)

    size = 0
    async with aiofiles.open(full, "wb") as f:
        while chunk := await file.read(CHUNK_SIZE):
            size += len(chunk)
            await f.write(chunk)

    record = File(
        name=file.filename,
        is_dir=False,
        size=size,
        storage_path=relative,
        owner_id=user.id,
        parent_id=parent_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


def resolve_path(storage_path: str) -> Path:
    return Path(settings.UPLOAD_DIR) / storage_path


async def get_download_file(db: AsyncSession, file_id: int, user: User) -> tuple[File, Path]:
    record = await get_file_by_id(db, file_id, user)
    if record is None or record.is_dir:
        raise FileNotFoundError

    path = resolve_path(record.storage_path)
    if not path.is_file():
        raise FileNotFoundError

    return record, path
