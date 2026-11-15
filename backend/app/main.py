from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .db import get_db
from .models import (
    AdminUser,
    GalleryItem,
    PriceCategory,
    PriceItem,
    ScrapeRun,
    SessionToken,
    SiteSetting,
)
from .schemas import (
    CategoryInput,
    CategoryResponse,
    LoginRequest,
    PasswordChange,
    PriceItemInput,
    PriceItemResponse,
    ReorderInput,
    SiteSettingsUpdate,
)
from .security import (
    SESSION_COOKIE,
    create_session,
    current_user,
    hash_token,
    normalize_phone,
    pwd_context,
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


@app.get("/api/v1/site-settings")
def site_settings(db: Session = Depends(get_db)) -> dict[str, str]:
    stored = {
        setting.key: setting.value for setting in db.scalars(select(SiteSetting)).all()
    }
    return {
        "business_name": "Jewel Essence Hair Studio",
        "address": "415 Wick Lane, London, United Kingdom, E3 2JG",
        "phone": "+44 7792 629696",
        "opening_hours": "Monday-Saturday, 09:00-19:00; Sunday closed",
        "instagram_url": "https://www.instagram.com/jewelessencehairstudio/",
        "booking_url": "https://book.squareup.com/appointments/8y0zkj85bj0rtj/location/LHHZMSJAZWKWF/services",
        **stored,
    }


@app.get("/api/v1/pricelist", response_model=list[CategoryResponse])
def public_pricelist(db: Session = Depends(get_db)) -> list[PriceCategory]:
    return db.scalars(
        select(PriceCategory)
        .where(PriceCategory.is_published)
        .options(selectinload(PriceCategory.items))
        .order_by(PriceCategory.sort_order)
    ).all()


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


@app.post("/api/v1/auth/login")
def login(
    payload: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> dict[str, bool]:
    user = db.scalar(
        select(AdminUser).where(
            AdminUser.phone_number == normalize_phone(payload.phone_number)
        )
    )
    if (
        not user
        or not user.is_active
        or not pwd_context.verify(payload.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    response.set_cookie(
        SESSION_COOKIE,
        create_session(db, user),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=28800,
    )
    return {"authenticated": True}


@app.post("/api/v1/auth/logout")
def logout(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> dict[str, bool]:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.get(SessionToken, hash_token(token))
        if session:
            db.delete(session)
            db.commit()
    response.delete_cookie(SESSION_COOKIE)
    return {"authenticated": False}


@app.get("/api/v1/auth/me")
def me(user: AdminUser = Depends(current_user)) -> dict[str, object]:
    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "must_change_password": user.must_change_password,
    }


@app.post("/api/v1/auth/change-password")
def change_password(
    payload: PasswordChange,
    user: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    if not pwd_context.verify(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = pwd_context.hash(payload.new_password)
    user.must_change_password = False
    db.commit()
    return {"changed": True}


@app.get("/api/v1/admin/pricelist/categories", response_model=list[CategoryResponse])
def admin_categories(
    _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> list[PriceCategory]:
    return db.scalars(
        select(PriceCategory)
        .options(selectinload(PriceCategory.items))
        .order_by(PriceCategory.sort_order)
    ).all()


@app.post("/api/v1/admin/pricelist/categories", response_model=CategoryResponse)
def create_category(
    payload: CategoryInput,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> PriceCategory:
    category = PriceCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.post("/api/v1/admin/pricelist/items", response_model=PriceItemResponse)
def create_item(
    payload: PriceItemInput,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> PriceItem:
    item = PriceItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/v1/admin/pricelist/items", response_model=list[PriceItemResponse])
def admin_items(
    _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> list[PriceItem]:
    return db.scalars(
        select(PriceItem).order_by(PriceItem.category_id, PriceItem.sort_order)
    ).all()


@app.patch(
    "/api/v1/admin/pricelist/categories/{category_id}", response_model=CategoryResponse
)
def update_category(
    category_id: int,
    payload: CategoryInput,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> PriceCategory:
    category = db.get(PriceCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump().items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@app.delete("/api/v1/admin/pricelist/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    category = db.get(PriceCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()


@app.patch("/api/v1/admin/pricelist/items/{item_id}", response_model=PriceItemResponse)
def update_item(
    item_id: int,
    payload: PriceItemInput,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> PriceItem:
    item = db.get(PriceItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/v1/admin/pricelist/items/{item_id}", status_code=204)
def delete_item(
    item_id: int, _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> None:
    item = db.get(PriceItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


@app.post("/api/v1/admin/pricelist/reorder")
def reorder_pricelist(
    payload: ReorderInput,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    for position, item_id in enumerate(payload.item_ids):
        item = db.get(PriceItem, item_id)
        if item:
            item.sort_order = position
    db.commit()
    return {"updated": True}


@app.patch("/api/v1/admin/site-settings")
def update_site_settings(
    payload: SiteSettingsUpdate,
    _: AdminUser = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    for key, value in payload.values.items():
        setting = db.get(SiteSetting, key) or SiteSetting(key=key, value=value)
        setting.value = value
        db.add(setting)
    db.commit()
    return site_settings(db)


@app.get("/api/v1/admin/site-settings")
def admin_site_settings(
    _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, str]:
    return site_settings(db)


@app.get("/api/v1/admin/scrape-runs")
def scrape_runs(
    _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> list[dict[str, object]]:
    runs = db.scalars(select(ScrapeRun).order_by(ScrapeRun.id.desc()).limit(30)).all()
    return [
        {
            "id": run.id,
            "status": run.status,
            "items_seen": run.items_seen,
            "error_summary": run.error_summary,
            "started_at": run.started_at,
        }
        for run in runs
    ]


@app.post("/api/v1/admin/scrape-runs")
def start_scrape_run(
    _: AdminUser = Depends(current_user), db: Session = Depends(get_db)
) -> dict[str, object]:
    run = ScrapeRun(
        status="disabled",
        items_seen=0,
        error_summary="Public-only scraping requires explicit legal and operational approval",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {
        "id": run.id,
        "status": run.status,
        "items_seen": run.items_seen,
        "error_summary": run.error_summary,
    }
