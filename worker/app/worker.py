"""Public-only, idempotent gallery synchronisation worker."""

import json
import os
from io import BytesIO
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import sleep
from typing import Callable
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image
from sqlalchemy import create_engine, text

MAX_ASSETS = 1000
DEFAULT_INTERVAL_SECONDS = 24 * 60 * 60
APIFY_API_URL = "https://api.apify.com/v2"
APIFY_POLL_INTERVAL_SECONDS = 5
APIFY_MAX_WAIT_SECONDS = 15 * 60


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


def _apify_request(
    method: str, url: str, token: str, payload: dict[str, object] | None = None
) -> dict[str, object] | list[object]:
    request_data = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        f"{url}?{urlencode({'token': token})}",
        data=request_data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urlopen(request, timeout=60) as response:
        result = json.loads(response.read())
    return result["data"] if isinstance(result, dict) and "data" in result else result


def _apify_records(item: dict[str, object]) -> list[dict[str, object]]:
    post_id = str(item.get("id") or item.get("pk") or item.get("shortCode") or "")
    children = item.get("childPosts") or item.get("images")
    posts = children if isinstance(children, list) and children else [item]
    records: list[dict[str, object]] = []

    for index, post in enumerate(posts):
        if not isinstance(post, dict):
            continue
        video_url = post.get("videoUrl") or post.get("video_url")
        image_url = post.get("displayUrl") or post.get("display_url")
        thumbnail_url = (
            post.get("thumbnailUrl") or post.get("thumbnail_url") or image_url
            if video_url
            else None
        )
        media_type = "video" if video_url else "image"
        source_url = video_url or image_url
        if not source_url:
            continue
        media_id = post.get("id") or post.get("pk") or post.get("shortCode")
        records.append(
            {
                "media_id": str(media_id or f"{post_id}_{index}"),
                "media_type": media_type,
                "source_url": str(source_url),
                "thumbnail_url": str(thumbnail_url) if thumbnail_url else None,
                "width": int(post.get("width") or 0),
                "height": int(post.get("height") or 0),
            }
        )
    return records


def _scraper_records() -> list[dict[str, object]]:
    username = os.getenv("INSTAGRAM_USERNAME", "jewelessencehairstudio")
    count = int(os.getenv("INSTAGRAM_COUNT", "40"))
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise ValueError("APIFY_API_TOKEN must be set when the scraper is enabled")
    actor_id = os.getenv("APIFY_ACTOR_ID", "apify/instagram-scraper")
    actor_url = f"{APIFY_API_URL}/acts/{quote(actor_id, safe='')}"
    run = _apify_request(
        "POST",
        f"{actor_url}/runs",
        token,
        {
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "resultsType": "posts",
            "resultsLimit": count,
        },
    )
    if not isinstance(run, dict):
        raise ValueError("Apify returned an invalid actor run response")
    run_id = run.get("id")
    dataset_id = run.get("defaultDatasetId")
    if not isinstance(run_id, str) or not isinstance(dataset_id, str):
        raise ValueError("Apify actor run response did not include run and dataset IDs")

    elapsed = 0
    while True:
        status_response = _apify_request(
            "GET", f"{APIFY_API_URL}/actor-runs/{quote(run_id, safe='')}", token
        )
        if not isinstance(status_response, dict):
            raise ValueError("Apify returned an invalid actor status response")
        status = status_response.get("status")
        if status == "SUCCEEDED":
            break
        if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
            raise RuntimeError(f"Apify actor run ended with status {status}")
        if elapsed >= APIFY_MAX_WAIT_SECONDS:
            raise TimeoutError("Apify actor run exceeded the maximum wait time")
        sleep(APIFY_POLL_INTERVAL_SECONDS)
        elapsed += APIFY_POLL_INTERVAL_SECONDS

    dataset = _apify_request(
        "GET",
        f"{APIFY_API_URL}/datasets/{quote(dataset_id, safe='')}/items",
        token,
    )
    if not isinstance(dataset, list):
        raise ValueError("Apify returned an invalid dataset response")

    unique: dict[str, dict[str, object]] = {}
    for item in dataset:
        if not isinstance(item, dict):
            continue
        for record in _apify_records(item):
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
        records = _scraper_records()
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


def run_forever(sleep_fn: Callable[[float], None] = sleep) -> None:
    interval = int(os.getenv("SCRAPER_INTERVAL_SECONDS", str(DEFAULT_INTERVAL_SECONDS)))
    if interval <= 0:
        raise ValueError("SCRAPER_INTERVAL_SECONDS must be greater than zero")

    while True:
        run()
        sleep_fn(interval)


if __name__ == "__main__":
    if os.getenv("SCRAPER_RUN_ONCE", "false").lower() == "true":
        run()
    else:
        run_forever()
