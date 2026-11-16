from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import (
    GalleryItem,
)

app = FastAPI(title="Jewel Essence Hair Studio API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.api_cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error
    return {"status": "ready"}


@app.get("/api/v1/gallery")
def gallery(db: Session = Depends(get_db)) -> dict[str, object]:
    items = db.scalars(
        select(GalleryItem)
        .where(GalleryItem.is_visible)
        .order_by(GalleryItem.id.desc())
        .limit(50)
    ).all()
    return {
        "items": [
            {
                "id": item.id,
                "media_type": item.media_type,
                "media_path": item.media_path,
                "thumbnail_path": item.thumbnail_path,
                "width": item.width,
                "height": item.height,
            }
            for item in items
        ],
        "next_cursor": None,
    }


@app.get("/api/v1/media/{media_path:path}")
def media(media_path: str) -> FileResponse:
    root = Path(settings.media_root).resolve()
    requested = (root / media_path).resolve()
    if root not in requested.parents or not requested.is_file():
        raise HTTPException(status_code=404, detail="Media not found")
    return FileResponse(requested)
