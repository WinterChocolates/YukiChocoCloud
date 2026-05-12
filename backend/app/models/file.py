from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_dir: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    size: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    owner = relationship("User", backref="files", lazy="selectin")
    parent = relationship("File", remote_side=[id], backref="children", lazy="selectin")
