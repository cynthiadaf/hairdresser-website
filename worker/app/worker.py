"""Public-only, idempotent gallery synchronisation worker."""

import json
import os
import subprocess
import tempfile
from io import BytesIO
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image
from sqlalchemy import create_engine, text

MAX_ASSETS = 1000


@dataclass(frozen=True)
class ScrapedMedia:
    media_id: str
    media_type: str
    source_url: str
    width: int
    height: int


@dataclass(frozen=True)
class ScrapeAudit:
    status: str
    items_seen: int
    assets_retained: int
    message: str


def content_key(media: ScrapedMedia) -> str:
    return sha256(f"{media.media_id}:{media.media_type}".encode()).hexdigest()


def retain_newest(paths: list[Path], limit: int = MAX_ASSETS) -> list[Path]:
    return sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def _records(value: object, parent_id: str = "") -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    if isinstance(value, dict):
        media_id = str(value.get("id") or parent_id)
        source_url = value.get("display_url") or value.get("thumbnail_src")
        if media_id and isinstance(source_url, str):
            dimension = value.get("dimension") or {}
            found.append(
                {
                    "media_id": media_id,
                    "media_type": "video" if value.get("is_video") else "image",
                    "source_url": source_url,
                    "thumbnail_url": value.get("thumbnail_src"),
                    "width": int(dimension.get("width") or 0),
                    "height": int(dimension.get("height") or 0),
                }
            )
        for child in value.values():
            found.extend(_records(child, media_id))
    elif isinstance(value, list):
        for child in value:
            found.extend(_records(child, parent_id))
    return found


def _scraper_records(output_dir: Path) -> list[dict[str, object]]:
    username = os.getenv("INSTAGRAM_USERNAME", "jewelessencehairstudio")
    count = os.getenv("INSTAGRAM_COUNT", "40")
    timeout = os.getenv("SCRAPER_TIMEOUT_MS", "1500")
    command = [
        os.getenv("INSTAGRAM_SCRAPER_BIN", "instatouch"),
        "user",
        username,
        "--count",
        count,
        "--mediaType",
        "all",
        "--filetype",
        "json",
        "--filepath",
        str(output_dir),
        "--filename",
        "feed",
        "--timeout",
        timeout,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
    files = sorted(output_dir.glob("feed*.json"))
    if not files:
        raise RuntimeError("Instagram scraper did not produce JSON output")
    payload = json.loads(files[-1].read_text(encoding="utf-8"))
    unique: dict[str, dict[str, object]] = {}
    for record in _records(payload):
        unique[str(record["media_id"])] = record
    return list(unique.values())


def _download(url: str) -> tuple[bytes, int, int]:
    request = Request(url, headers={"User-Agent": "JewelEssenceGallery/1.0"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    with Image.open(BytesIO(content)) as image:
        image.verify()
    with Image.open(BytesIO(content)) as image:
        return content, image.width, image.height


def _save_media(
    record: dict[str, object], media_root: Path
) -> tuple[str, str | None, int, int]:
    media_id = str(record["media_id"])
    media_type = str(record["media_type"])
    source_url = str(
        record.get("thumbnail_url")
        if media_type == "video" and record.get("thumbnail_url")
        else record["source_url"]
    )
    content, width, height = _download(source_url)
    relative_path = (
        Path("gallery")
        / f"{content_key(ScrapedMedia(media_id, media_type, source_url, width, height))}.jpg"
    )
    destination = media_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    path = relative_path.as_posix()
    return path, path if media_type == "video" else None, width, height


def _database_url() -> str | None:
    return os.getenv("DATABASE_URL")


def _persist(audit: ScrapeAudit, items: list[dict[str, object]]) -> None:
    database_url = _database_url()
    if not database_url:
        return
    engine = create_engine(database_url)
    with engine.begin() as connection:
        for item in items:
            connection.execute(
                text(
                    "INSERT INTO gallery_items "
                    "(instagram_media_id, media_type, media_path, thumbnail_path, width, height, is_visible) "
                    "VALUES (:media_id, :media_type, :media_path, :thumbnail_path, :width, :height, true) "
                    "ON CONFLICT (instagram_media_id) DO UPDATE SET "
                    "media_path = EXCLUDED.media_path, thumbnail_path = EXCLUDED.thumbnail_path, "
                    "width = EXCLUDED.width, height = EXCLUDED.height, is_visible = true"
                ),
                item,
            )
        connection.execute(
            text(
                "INSERT INTO scrape_runs (status, items_seen, error_summary) "
                "VALUES (:status, :items_seen, :error_summary)"
            ),
            {
                "status": audit.status,
                "items_seen": audit.items_seen,
                "error_summary": audit.message,
            },
        )


def _retain(media_root: Path) -> int:
    paths = (
        list((media_root / "gallery").glob("*"))
        if (media_root / "gallery").exists()
        else []
    )
    retained = retain_newest(paths)
    retained_set = set(retained)
    for path in paths:
        if path not in retained_set:
            path.unlink(missing_ok=True)
    return len(retained)


def run() -> ScrapeAudit:
    if os.getenv("SCRAPER_ENABLED", "false").lower() != "true":
        audit = ScrapeAudit("disabled", 0, 0, "set SCRAPER_ENABLED=true to run")
        print(f"scraper status={audit.status}: {audit.message}")
        return audit

    media_root = Path(os.getenv("MEDIA_ROOT", "/data/media"))
    try:
        with tempfile.TemporaryDirectory(prefix="instagram-") as temporary_dir:
            records = _scraper_records(Path(temporary_dir))
        stored: list[dict[str, object]] = []
        for record in records:
            media_path, thumbnail_path, width, height = _save_media(record, media_root)
            stored.append(
                {
                    "media_id": record["media_id"],
                    "media_type": record["media_type"],
                    "media_path": media_path,
                    "thumbnail_path": thumbnail_path,
                    "width": width,
                    "height": height,
                }
            )
        retained = _retain(media_root)
        audit = ScrapeAudit("success", len(records), retained, "")
        _persist(audit, stored)
    except Exception as error:
        audit = ScrapeAudit("failed", 0, 0, str(error)[:500])
        try:
            _persist(audit, [])
        except Exception:
            pass
    print(
        f"scraper status={audit.status} items_seen={audit.items_seen} "
        f"assets_retained={audit.assets_retained}: {audit.message}"
    )
    return audit


if __name__ == "__main__":
    run()
