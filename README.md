# Jewel Essence Hair Studio

Local-first monorepo for the Jewel Essence Hair Studio website.

## Services

- `frontend/`: Angular TypeScript public site and staff route shell, built and served by Nginx in Compose.
- `backend/`: FastAPI API, secure cookie session foundation, SQLAlchemy models, and Alembic migration.
- `worker/`: credential-free public-only gallery worker using the approved `instatouch` scraper, media validation, audit records, deduplication, and retention.
- PostgreSQL and persistent media volumes are defined in `docker-compose.yml`.

## Local development

1. Copy `.env.example` to `.env` and set local-only secrets.
2. Start PostgreSQL with `docker compose up db`.
3. Run the API from `backend/` with `uvicorn app.main:app --reload`.
4. Run the frontend from `frontend/` with `npm install` and `npm start`.
5. Apply schema migrations with `alembic upgrade head` from `backend/`.

To run the complete containerized stack, copy `.env.example` to `.env` and run `docker compose up --build`. The frontend is available at `http://localhost` by default, or at the port configured by `FRONTEND_PORT`. Nginx serves the Angular application, falls back to `index.html` for client routes, and proxies `/api/` to the FastAPI container, so the same setup can be placed behind a Droplet reverse proxy and custom domain.

Backend tests are in `backend/tests`. After legal approval, set `SCRAPER_ENABLED=true` in `.env` and run `docker compose run --rm worker` for a one-shot public-only gallery sync. The worker does not accept Instagram credentials, retains only image files and video thumbnails, and records each run in PostgreSQL. No fabricated assets, contact form, or Square API integration are included.
