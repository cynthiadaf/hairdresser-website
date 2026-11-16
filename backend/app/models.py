from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class GalleryItem(Base):
    __tablename__ = "gallery_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_media_id: Mapped[str] = mapped_column(
        String(160), unique=True, index=True
    )
    media_type: Mapped[str] = mapped_column(String(20))
    media_path: Mapped[str] = mapped_column(String(500))
    thumbnail_path: Mapped[str | None] = mapped_column(String(500))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(30))
    items_seen: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
