import os
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.file import File
from app.models.user import User


async def list_files(db: AsyncSession, user: User, parent_id: int | None) -> list[File]:
    query = (
        select(File)
        .where(File.owner_id == user.id, File.is_deleted == False, File.parent_id == parent_id)
        .order_by(File.is_dir.desc(), File.name)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_file_by_id(db: AsyncSession, file_id: int, user: User) -> File | None:
    result = await db.execute(
        select(File).where(File.id == file_id, File.owner_id == user.id, File.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def create_folder(db: AsyncSession, user: User, name: str, parent_id: int | None) -> File:
    if parent_id is not None:
        parent = await get_file_by_id(db, parent_id, user)
        if parent is None or not parent.is_dir:
            raise ValueError("Parent directory not found")

    folder = File(name=name, is_dir=True, owner_id=user.id, parent_id=parent_id)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def delete_file(db: AsyncSession, file_id: int, user: User) -> File:
    file = await get_file_by_id(db, file_id, user)
    if file is None:
        raise FileNotFoundError

    # 删除物理文件
    if not file.is_dir and file.storage_path:
        physical_path = Path(settings.UPLOAD_DIR) / file.storage_path
        if physical_path.is_file():
            os.remove(physical_path)

    # 如果是文件夹，递归删除所有子文件的物理文件
    if file.is_dir:
        await _delete_children_physical(db, file.id, user)

    file.is_deleted = True
    await db.commit()
    return file


async def _delete_children_physical(db: AsyncSession, parent_id: int, user: User):
    """递归删除文件夹下所有子文件的物理文件"""
    query = select(File).where(
        File.parent_id == parent_id,
        File.owner_id == user.id,
        File.is_deleted == False
    )
    result = await db.execute(query)
    children = list(result.scalars().all())

    for child in children:
        if not child.is_dir and child.storage_path:
            physical_path = Path(settings.UPLOAD_DIR) / child.storage_path
            if physical_path.is_file():
                os.remove(physical_path)
        elif child.is_dir:
            await _delete_children_physical(db, child.id, user)

        child.is_deleted = True


async def get_storage_used(db: AsyncSession, user: User) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(File.size), 0)).where(
            File.owner_id == user.id,
            File.is_dir == False,
            File.is_deleted == False,
        )
    )
    return result.scalar_one()
