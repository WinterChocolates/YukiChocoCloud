from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Share(Base):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    file = relationship("File", backref="shares", lazy="selectin")
