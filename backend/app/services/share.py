import uuid
from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.models.share import Share
from app.models.user import User
from app.services.files import get_file_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _generate_token() -> str:
    return uuid.uuid4().hex


async def create_share(
    db: AsyncSession,
    user: User,
    file_id: int,
    password: str | None,
    expire_at: datetime | None,
) -> Share:
    file = await get_file_by_id(db, file_id, user)
    if file is None:
        raise FileNotFoundError

    hashed = pwd_context.hash(password) if password else None

    share = Share(
        file_id=file_id,
        token=_generate_token(),
        password=hashed,
        expire_at=expire_at,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)
    return share


async def get_share_by_token(db: AsyncSession, token: str) -> Share | None:
    result = await db.execute(select(Share).where(Share.token == token))
    return result.scalar_one_or_none()


async def list_shares_by_file(db: AsyncSession, user: User, file_id: int) -> list[Share]:
    file = await get_file_by_id(db, file_id, user)
    if file is None:
        raise FileNotFoundError
    result = await db.execute(
        select(Share).where(Share.file_id == file_id).order_by(Share.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_share(db: AsyncSession, user: User, share_id: int) -> bool:
    result = await db.execute(select(Share).where(Share.id == share_id))
    share = result.scalar_one_or_none()
    if share is None:
        return False
    file = await get_file_by_id(db, share.file_id, user)
    if file is None:
        return False
    await db.delete(share)
    await db.commit()
    return True


async def access_share(db: AsyncSession, token: str, password: str | None) -> File:
    share = await get_share_by_token(db, token)
    if share is None:
        raise FileNotFoundError

    now = datetime.now(timezone.utc)
    if share.expire_at is not None and share.expire_at.replace(tzinfo=timezone.utc) < now:
        raise PermissionError("Share link has expired")

    if share.password is not None:
        if password is None or not pwd_context.verify(password, share.password):
            raise PermissionError("Invalid password")

    result = await db.execute(select(File).where(File.id == share.file_id, File.is_deleted == False))
    file = result.scalar_one_or_none()
    if file is None:
        raise FileNotFoundError

    return file
