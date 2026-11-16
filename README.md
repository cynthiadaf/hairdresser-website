# Jewel Essence Hair Studio

Local-first monorepo for the Jewel Essence Hair Studio website.

## Services

- `frontend/`: Angular TypeScript public site, built and served by Nginx in Compose.
- `backend/`: FastAPI gallery API, SQLAlchemy models, and Alembic migration.
- `worker/`: credential-free public-only gallery worker using Instaloader, media validation, audit records, deduplication, and retention.
- PostgreSQL and persistent media volumes are defined in `docker-compose.yml`.

## Local development

1. Copy `.env.example` to `.env` and set local-only secrets.
2. Start PostgreSQL with `docker compose up db`.
3. Run the API from `backend/` with `uvicorn app.main:app --reload`.
4. Run the frontend from `frontend/` with `npm install` and `npm start`.
5. Apply schema migrations with `alembic upgrade head` from `backend/`.

To run the complete containerized stack, copy `.env.example` to `.env` and run `docker compose up --build`. The frontend is available at `http://localhost` by default, or at the port configured by `FRONTEND_PORT`. Nginx serves the Angular application, falls back to `index.html` for client routes, and proxies `/api/` to the FastAPI container, so the same setup can be placed behind a Droplet reverse proxy and custom domain.

Backend tests are in `backend/tests`. After legal approval, set `SCRAPER_ENABLED=true` in `.env` and run the complete Compose stack. The worker performs a public-only gallery sync immediately on startup, then repeats it every 24 hours. Set `SCRAPER_INTERVAL_SECONDS` to override the interval, or `SCRAPER_RUN_ONCE=true` for a one-shot sync. The worker uses Instaloader's public profile API and does not accept Instagram credentials. It retains only image files and video thumbnails, and records gallery metadata and each run in PostgreSQL. Contact details are hardcoded in the frontend, and services and prices link directly to Square.
