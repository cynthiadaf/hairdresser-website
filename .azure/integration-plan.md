# Integration hand-off

## Backend
- Folder: `backend/`
- Run: `uvicorn app.main:app --reload --port 8000`
- Build: `docker build -t jewel-essence-api backend`
- Health: `GET /api/v1/health`; readiness: `GET /api/v1/ready`

## Frontend
- Folder: `frontend/`
- Run: `npm start`
- Build: `npm run build`
- API seam: add `src/app/core/api.service.ts`; replace page placeholders with typed HTTP calls to `/api/v1`.
- Mock assets: none supplied; do not invent logo, map, or gallery media.

## API inventory
- Public: `GET /api/v1/health`, `/ready`, `/site-settings`, `/pricelist`, `/gallery`
- Auth: `POST /api/v1/auth/login`, `/logout`, `GET /api/v1/auth/me`, `POST /api/v1/auth/change-password`
- Admin: `GET/POST /api/v1/admin/pricelist/categories`, `POST /api/v1/admin/pricelist/items`, `PATCH /api/v1/admin/site-settings`, `GET /api/v1/admin/scrape-runs`

## Database
- PostgreSQL in Compose; SQLAlchemy + Alembic in `backend/migrations/`.
- Connection: `DATABASE_URL`; media: `MEDIA_ROOT`.
- Create migrations with `alembic revision --autogenerate`; apply with `alembic upgrade head`.
- No seed data. Bootstrap admin must be a future protected command using secrets.

## Worker
- Folder: `worker/`; command `python -m app.worker`.
- Public-only, credential-free Instagram adapter remains intentionally disabled pending approval.
- Idempotency key and bounded retention helpers are in `worker/app/worker.py`.
