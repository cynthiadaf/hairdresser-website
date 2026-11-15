# Jewels Essence Hair Studio Website

**Status**: Planning  
**Created**: 2026-11-15  
**Mode**: Manual approval required before scaffolding  

## 1. Project Summary

Create a polished, responsive hairdresser website for Jewels Essence Hair Studio. The public experience has Home, Pricelist, Gallery, and Contact Us pages. A deliberately unobtrusive footer link opens a private hairdresser login. The authenticated operator can edit the pricelist and change her password. Gallery images are synchronized daily from the studio's Instagram account, while the public site remains fast and independent of live Instagram availability.

The repository currently contains only a README and Git metadata; there is no existing application, infrastructure, database schema, or CI pipeline to preserve.

## 2. Goals, Scope & Acceptance Criteria

### Goals

- Deliver an elegant, classy, minimalist Angular website with strong mobile and desktop layouts.
- Provide a Python FastAPI API and a separate scheduled Python scraper worker.
- Make public content read-only and available without login.
- Provide secure email/password administration for pricelist editing and password changes.
- Keep gallery images locally/privately stored and serve optimized derivatives.
- Build, test, containerize, and deploy reproducibly through GitHub Actions.

### In scope

- Home, Pricelist, Gallery, Contact Us, login, admin pricelist editor, and password-change screens.
- Contact details, external links, map image, social link, booking link, and dynamic `© Xertz Industries <current year>` footer.
- PostgreSQL persistence, object/blob media storage, migrations, API documentation, health checks, scrape audit records, and observability hooks.
- Daily scheduled Instagram synchronization using `drawrowfly/instagram-scraper`, subject to legal and operational approval.

### Out of scope

- Public contact form, customer accounts, payments, appointment booking implementation, CMS, multi-staff roles, or real-time Instagram embedding.
- Copying Square's booking/pricelist system. Square is treated as a source to review and link to, not as an undocumented API dependency.

### Acceptance criteria

1. All public routes render responsively and meet keyboard, focus, semantic HTML, and WCAG-oriented contrast requirements.
2. Public pricelist and gallery data load from the API, with graceful loading/error/empty states.
3. Only an authenticated hairdresser can create, edit, reorder, publish/unpublish, or archive pricelist categories/items.
4. Passwords are hashed; login has rate limiting, secure cookies, CSRF protection as applicable, and generic failure messages.
5. A daily worker run is idempotent, records a run outcome, deduplicates media, and does not break the public site when Instagram is unavailable.
6. CI runs linting, unit tests, API tests, frontend tests, build, container build, and vulnerability checks.

## 3. Assumptions & Decisions Requiring Confirmation

### Assumptions

- The requested business is Jewels Essence Hair Studio and the Instagram account is public and authorized for this use.
- One administrator account is sufficient for the first release.
- DigitalOcean Managed PostgreSQL and S3-compatible object storage are appropriate; DigitalOcean Spaces is the recommended production media store.
- The map image will be supplied by the owner or generated from a licensed/static-map provider; no unlicensed screenshot will be committed.
- Square's page is the authoritative reference for initial service names/prices only after the owner confirms permission and currency/tax conventions.
- The booking URL can be linked externally; no Square credentials or private API access are needed.

### Decisions needing user approval before implementation

- Exact business address, phone, email, opening hours, social links, booking URL, logo, brand colors, typography, and map asset.
- Initial admin email and a secure bootstrap-password delivery process.
- Whether to store downloaded Instagram originals or only resized derivatives, maximum gallery count, retention period, and whether captions/alt text may be displayed.
- Droplet sizing, region, firewall rules, and whether the frontend is served from the Droplet or another static host.
- Whether the scraper may use Instagram credentials/session cookies. Default recommendation is no credentials and public-only scraping.
- Whether to use a managed WAF/CDN and custom domain in the first release.

## 4. Architecture & Service Boundaries

### Services

1. **Angular frontend**: static production bundle served by Nginx or a static-hosting service; communicates only with versioned HTTPS API endpoints.
2. **FastAPI backend**: public read APIs, admin authentication, protected pricelist mutation APIs, site configuration, media URLs, scrape status, and health/readiness endpoints.
3. **Python scraper worker**: scheduled container/command using `drawrowfly/instagram-scraper`; downloads approved public media, validates content, stores blobs and metadata, and writes audit results.
4. **PostgreSQL**: relational source of truth for users, pricelist, configuration, gallery metadata, and job runs.
5. **Blob/object storage**: private originals/derivatives; API returns short-lived signed URLs or an image proxy.

### Request and data flow

- Browser → HTTPS reverse proxy → Angular static assets.
- Browser → HTTPS `/api/v1` → FastAPI → PostgreSQL/blob storage.
- Scheduler → scraper container → Instagram (outbound only) → blob storage/PostgreSQL.
- API never proxies arbitrary external URLs; it returns allow-listed media references.

### Recommended production topology

A hardened DigitalOcean Droplet running Docker Compose for the Angular frontend, FastAPI API, and scheduled scraper worker; DigitalOcean Managed PostgreSQL for relational data; and DigitalOcean Spaces for private gallery originals/derivatives. Publish versioned images to GitHub Container Registry or DigitalOcean Container Registry. Use Cloudflare DNS and proxying for `jewelessencehairstudio.co.uk`, with HTTPS, caching, WAF/rate limiting where appropriate, and separate `www` and `api` hostnames routed to the Droplet. Run the worker through a host-managed cron or systemd timer that invokes a one-shot worker container, with locking to prevent overlapping runs. Store secrets in protected GitHub Actions environments for deployment and in a root-readable Droplet environment/secrets file outside the repository; rotate deployment credentials and restrict firewall access to SSH, HTTP, and HTTPS.

## 5. Data Model & API Contract

### Core tables

- `admin_users`: `id`, `email`, `password_hash`, `role`, `is_active`, `created_at`, `updated_at`, `last_login_at`, `password_changed_at`.
- `refresh_tokens` (or server-side sessions): hashed token/session ID, user, expiry, revocation timestamp, device metadata.
- `pricelist_categories`: `id`, `name`, `description`, `sort_order`, `is_published`, timestamps.
- `pricelist_items`: `id`, category ID, name, description, duration_minutes, price_minor, currency, sort_order, is_published, timestamps.
- `site_settings`: singleton/key-value records for address, phone, email, hours, links, map blob key, and booking URL.
- `gallery_items`: stable Instagram media ID, permalink, caption, published timestamp, blob keys, width/height, checksum, alt text, visibility, timestamps.
- `scrape_runs`: start/end, status, counts, error summary, scraper version, source account, timestamps.
- `audit_events`: actor, action, resource, request correlation ID, timestamp; never store passwords or session secrets.

Use Alembic migrations, UTC timestamps, integer minor currency units, database constraints, indexes on published/sort fields and Instagram IDs, and soft deletion where auditability matters.

### API routes

Public:

- `GET /api/v1/health`, `GET /api/v1/ready`
- `GET /api/v1/site-settings`
- `GET /api/v1/pricelist`
- `GET /api/v1/gallery?cursor=&limit=`

Authentication:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

Protected admin:

- `GET/POST /api/v1/admin/pricelist/categories`
- `PATCH/DELETE /api/v1/admin/pricelist/categories/{id}`
- `GET/POST /api/v1/admin/pricelist/items`
- `PATCH/DELETE /api/v1/admin/pricelist/items/{id}`
- `POST /api/v1/admin/pricelist/reorder`
- `GET /api/v1/admin/scrape-runs`
- `POST /api/v1/admin/scrape-runs` (manual run, rate-limited)

Return consistent problem-details errors, OpenAPI schemas, pagination metadata, validation messages safe for users, and correlation IDs.

## 6. Design System & UI

**Component Library**: Angular Material (customized theme)  
**Visual direction**: Elegant, restrained, editorial, generous whitespace, warm neutrals, charcoal text, one muted metallic/accent color, fine borders, and high-quality image cropping. Avoid excessive animation and visual clutter.  
**Typography**: Pair a refined display serif with a highly legible sans-serif body font; self-host or use a properly licensed provider.  
**Layout**: Mobile-first responsive grid, max-width content container, sticky/compact header, prominent but calm calls to action, and consistent vertical rhythm.  
**Accessibility**: Visible focus rings, skip link, semantic headings, reduced-motion support, alt text from curated metadata, keyboard-operable dialogs/forms, and adequate contrast.  
**Component Library Defaults**: Angular Material components for buttons, navigation, cards, tables, dialogs, snackbars, form fields, menus, progress indicators, and responsive sidenav; use CSS for brand-specific composition rather than raw repeated controls.

### Frontend routes and components

- `/`: `HomePage` with hero, value proposition, featured services, gallery teaser, booking CTA.
- `/pricelist`: `PricelistPage`, category sections, service duration/price, Square booking link.
- `/gallery`: `GalleryPage`, responsive image grid/lightbox, pagination and empty/error states.
- `/contact`: `ContactPage`, details, hours, social/booking links, accessible map image and attribution.
- `/staff/login`: `StaffLoginPage`; reachable only from a low-emphasis footer link and direct URL.
- `/staff/pricelist`: `PricelistEditorPage`, category/item CRUD, reorder, publish state, optimistic-safe save feedback.
- `/staff/password`: `ChangePasswordPage`, current/new/confirmation validation, logout-after-change policy.

Shared components: `SiteHeader`, `SiteFooter`, `BookingButton`, `LoadingState`, `ErrorState`, `ConfirmDialog`, `ImageLightbox`, `AuthGuard`, `UnsavedChangesGuard`, and API/interceptor services.

## 7. Security, Privacy & Operational Risks

- Hash passwords with Argon2id/bcrypt; never log credentials. Bootstrap the first account through a one-time secret or operator CLI.
- Prefer secure, HttpOnly, SameSite cookies with short-lived sessions, CSRF tokens, rotation/revocation, and HTTPS-only production cookies. If stateless tokens are selected, use short-lived access tokens and rotated refresh tokens stored hashed.
- Rate-limit login/manual scrape routes, enforce generic login errors, add lockout/backoff, validate all input server-side, and configure strict CORS, CSP, HSTS, frame and MIME protections.
- Keep database, Spaces, session, and scraper credentials in a root-readable Droplet secrets file outside the repository, with GitHub Actions protected-environment secrets limited to deployment. No secrets may appear in the repository, Docker layers, logs, or frontend bundles. Prefer narrowly scoped deployment credentials, firewall-restricted SSH keys, and regular credential rotation. Do not expose PostgreSQL directly to the public internet; allow only the Droplet's private/network access and an explicitly controlled administrator path.
- Instagram scraping can violate Instagram terms, robots expectations, rate limits, or account rules; obtain owner/legal approval, use public data only by default, throttle, cache, identify the user agent, provide a kill switch, and be prepared to replace it with an approved feed/API.
- Scraped media/captions and the map image may have copyright/privacy restrictions. Store only approved media, preserve attribution where required, obtain map-image license/attribution, and support takedown/deletion.
- Square content may change; do not scrape it in production without permission. Treat manual entry/import as the source of truth and link to Square for booking.
- Defend image processing against oversized files, malformed content, SSRF, path traversal, and decompression bombs; enforce MIME/size limits and malware scanning if uploads are later added.

## 8. Testing & Quality Plan

- Backend unit tests for pricing validation, auth/session policy, authorization, scraper deduplication, retry/backoff, and settings.
- API integration tests with disposable PostgreSQL and blob emulator; contract tests generated from OpenAPI.
- Angular unit/component tests, route-guard tests, HTTP interceptor tests, and Playwright end-to-end tests for public navigation, login, edit, password change, and error states.
- Worker tests with mocked Instagram responses, fixture media, rate-limit/error scenarios, idempotent reruns, and retention.
- Accessibility checks with axe/Playwright; responsive smoke tests at mobile/tablet/desktop breakpoints.
- CI security scans for dependencies, containers, secrets, and static analysis; backup/restore and migration rehearsal before production.

## 9. Local Development & Delivery

### Local development

Provide `docker-compose.yml` for PostgreSQL, an S3-compatible local object store such as MinIO, API, worker, and optional frontend dev proxy. Include `.env.example` containing placeholders only, Make/PowerShell-friendly commands, Alembic migration commands, seed-free bootstrap-admin command, and documented test commands. Angular uses `ng serve`; FastAPI uses Uvicorn reload; worker supports a one-shot local scrape against fixtures/mock mode.

### CI/CD

GitHub Actions should run on pull requests and protected-branch pushes:

1. Install/cache Node and Python dependencies.
2. Format/lint/type-check frontend, backend, and worker.
3. Run unit/integration/E2E tests and accessibility smoke checks.
4. Run dependency, secret, SAST, and container scans.
5. Build versioned frontend/API/worker images and publish to GHCR or DigitalOcean Container Registry.
6. Deploy only from protected environments after approval; connect to the Droplet using a restricted deployment key or approved DigitalOcean API workflow, pull the immutable image versions, run migrations as a controlled release step, then health-check and smoke-test.
7. Roll back by redeploying the previous image versions without destructive database rollback; use backward-compatible migrations.

## 10. Deployment Options, Milestones & Handoff

### Options

1. **Recommended**: DigitalOcean Droplet running Docker Compose + Managed PostgreSQL + Spaces + GitHub Actions, with Cloudflare DNS/proxy for `jewelessencehairstudio.co.uk`. This supports the API, frontend, and scheduled worker on one controlled host.
2. **Alternative**: A separate Droplet for the worker or frontend if resource usage, isolation, or availability requirements grow. This adds cost and operational complexity but reduces contention between workloads.
3. **Portable**: Any Docker host with managed PostgreSQL/object storage and cron. Lowest DigitalOcean coupling, but more responsibility for deployment, TLS, secrets, backups, and monitoring.

### Milestones

1. Confirm assumptions/assets, legal approval for Instagram/map, production option, and initial content.
2. Scaffold repository structure and Docker Compose; create migrations and API contract.
3. Implement API/auth/admin and Angular public/admin routes.
4. Implement gallery storage, worker, retention, and audit/status UI.
5. Apply visual polish, accessibility, tests, security hardening, and performance budgets.
6. Harden the Droplet, configure Docker Compose and scheduled worker execution, set up GitHub Actions deployment, Cloudflare DNS/HTTPS/custom-domain routing, backups/monitoring, owner acceptance, and production release.

### Definition of ready for scaffold

This plan is implementation-ready once the user confirms the decisions in Section 3, supplies brand/contact/map details, and explicitly approves this plan. The next agent must read this file and scaffold only after approval; it must not silently introduce a contact form, live Square integration, Instagram credentials, or unsupported identity provider.
