# Jewel Essence Hair Studio Website

**Status**: Approved  
**Created**: 2026-11-15  
**Mode**: Manual approval required before scaffolding  

## 1. Project Summary

Create a polished, responsive hairdresser website for Jewel Essence Hair Studio. The public experience has Home, Pricelist, Gallery, and Contact Us pages. A deliberately unobtrusive footer link opens a private hairdresser login. The authenticated operator can edit the pricelist and change her password. Gallery images are synchronized daily from the studio's Instagram account, while the public site remains fast and independent of live Instagram availability.

The repository currently contains only a README and Git metadata; there is no existing application, infrastructure, database schema, or CI pipeline to preserve.

## 2. Goals, Scope & Acceptance Criteria

### Goals

- Deliver an elegant, classy, minimalist Angular website with strong mobile and desktop layouts.
- Provide a Python FastAPI API and a separate scheduled Python scraper worker.
- Make public content read-only and available without login.
- Provide secure phone-number/password administration for pricelist editing, business-settings editing, and password changes.
- Keep gallery images locally/privately stored and serve them at near-original Instagram dimensions and quality.
- Build, test, containerize, and deploy reproducibly through GitHub Actions.

### In scope

- Home, Pricelist, Gallery, Contact Us, login, admin pricelist editor, and password-change screens.
- Contact details, external links, map image, social link, booking link, editable business settings, and dynamic `© Xertz Industries <current year>` footer.
- PostgreSQL persistence, Droplet-backed media storage, migrations, API documentation, health checks, scrape audit records, and observability hooks.
- Daily scheduled Instagram synchronization using `drawrowfly/instagram-scraper`, subject to legal and operational approval.

### Out of scope

- Public contact form, customer accounts, payments, appointment booking implementation, CMS, multi-staff roles, or real-time Instagram embedding.
- Copying Square's booking/pricelist system. Square is treated as a source to review and link to, not as an undocumented API dependency.

### Acceptance criteria

1. All public routes render responsively and meet keyboard, focus, semantic HTML, and WCAG-oriented contrast requirements.
2. Public pricelist and gallery data load from the API, with graceful loading/error/empty states.
3. Only an authenticated hairdresser can create, edit, reorder, publish/unpublish, or archive pricelist categories/items.
4. Passwords are hashed; phone-number login has rate limiting, secure cookies, CSRF protection as applicable, and generic failure messages.
5. A daily worker run is idempotent, records a run outcome, deduplicates media, and does not break the public site when Instagram is unavailable.
6. CI runs linting, unit tests, API tests, frontend tests, build, container build, and vulnerability checks.

## 3. Assumptions & Decisions Requiring Confirmation

### Assumptions

- The requested business is Jewel Essence Hair Studio and the Instagram account is public and authorized for this use.
- One administrator account is sufficient for the first release, authenticated by phone number and password rather than email.
- DigitalOcean Managed PostgreSQL and the Droplet's persistent disk are appropriate for the expected small gallery volume. Store downloaded images and generated video thumbnails on the server; do not retain full video files.
- The owner has supplied the logo and a map image for the Contact Us page. The production assets must be stored locally with appropriate permission/attribution rather than relying on an expiring Instagram CDN URL.
- Square's page is the authoritative reference for initial service names/prices only after the owner confirms permission and currency/tax conventions.
- The booking URL can be linked externally; no Square credentials or private API access are needed.

### Decisions needing user approval before implementation

- Whether the scraper may use Instagram credentials/session cookies. **Approved decision**: no credentials and public-only scraping.

### Deferred until deployment

- Droplet sizing, region, firewall rules, and whether the frontend is served from the Droplet or another static host.
- Managed WAF/CDN configuration and custom-domain routing.
- Production deployment, backups, monitoring, and release topology.

The first implementation phase is local-first: run the Angular frontend, FastAPI API, PostgreSQL, media volume, and scraper worker with Docker Compose on the developer machine. Deployment decisions will be finalized after the local site is working and reviewed.

### Confirmed business content

- **Business**: Jewel Essence Hair Studio.
- **Address**: 415 Wick Lane, London, United Kingdom, E3 2JG.
- **Phone**: +44 7792 629696.
- **Opening hours**: Monday-Saturday, 09:00-19:00; Sunday closed.
- **Instagram**: `https://www.instagram.com/jewelessencehairstudio/`.
- **Booking**: `https://book.squareup.com/appointments/8y0zkj85bj0rtj/location/LHHZMSJAZWKWF/services`.
- **Email**: blank initially; editable later through the staff settings screen.
- **Initial admin**: use `+44 7792 629696` as the login phone number; bootstrap the account through protected GitHub Actions secrets and require a password change after first login.
- **Brand direction**: black and white, based on the supplied logo, with logo-inspired editorial typography and restrained styling.
- **Map**: use the supplied map image on the Contact Us page, with attribution or licensing retained if required.
- **Gallery policy**: retain up to 1,000 gallery assets; download every image in a carousel; preserve image dimensions as supplied by Instagram without upscaling or aggressive recompression; generate one thumbnail per video at the source aspect ratio and a similar quality level; do not retain full videos, scrape captions, or create gallery alt-text metadata.

## 4. Architecture & Service Boundaries

### Services

1. **Angular frontend**: static production bundle served by Nginx or a static-hosting service; communicates only with versioned HTTPS API endpoints.
2. **FastAPI backend**: public gallery, media, health, and readiness APIs.
3. **Python scraper worker**: scheduled container/command using Apify's `apify/instagram-scraper` for public profile discovery; downloads every approved image in each carousel, generates one thumbnail for each approved video without retaining the full video, validates media, stores files and metadata, removes the oldest assets when the 1,000-asset limit is exceeded, and writes audit results.
4. **PostgreSQL**: relational source of truth for gallery metadata and scrape-run records.
5. **Droplet media volume**: persistent, non-public image files and generated video thumbnails mounted into the API/worker containers. The API serves media through an allow-listed route or Nginx, never by exposing arbitrary filesystem paths.

### Request and data flow

- Browser → HTTPS reverse proxy → Angular static assets.
- Browser → HTTPS `/api/v1` → FastAPI → PostgreSQL and the private Droplet media volume.
- Scheduler → scraper container → Instagram (outbound only) → Droplet media volume/PostgreSQL.
- API never proxies arbitrary external URLs; it returns allow-listed media references.

### Recommended production topology

A hardened DigitalOcean Droplet running Docker Compose for the Angular frontend, FastAPI API, and scheduled scraper worker; DigitalOcean Managed PostgreSQL for relational data; and a dedicated persistent media directory on the Droplet for approved images and generated video thumbnails. Publish versioned images to GitHub Container Registry or DigitalOcean Container Registry. Use Cloudflare DNS and proxying for `jewelessencehairstudio.co.uk`, with HTTPS, caching, WAF/rate limiting where appropriate, and separate `www` and `api` hostnames routed to the Droplet. Run the worker through a host-managed cron or systemd timer that invokes a one-shot worker container, with locking to prevent overlapping runs. Set disk quotas/alerts and scheduled backups for the media directory. Store secrets in protected GitHub Actions environments for deployment and in a root-readable Droplet environment/secrets file outside the repository; rotate deployment credentials and restrict firewall access to SSH, HTTP, and HTTPS.

## 5. Data Model & API Contract

### Core tables

- `gallery_items`: stable Instagram media ID plus carousel item key, media type, permalink, published timestamp, image path, thumbnail path, width/height, file size, checksum, visibility, timestamps. Carousel items retain their source ordering and are removed together where possible.
- `scrape_runs`: start/end, status, counts, error summary, scraper version, source account, timestamps.

Use Alembic migrations, UTC timestamps, integer minor currency units, database constraints, indexes on published/sort fields and Instagram IDs, and soft deletion where auditability matters.

### API routes

Public:

- `GET /api/v1/health`, `GET /api/v1/ready`
- `GET /api/v1/gallery?cursor=&limit=`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

Protected admin:

- `GET/POST /api/v1/admin/pricelist/categories`
- `PATCH/DELETE /api/v1/admin/pricelist/categories/{id}`
- `GET/POST /api/v1/admin/pricelist/items`
- `PATCH/DELETE /api/v1/admin/pricelist/items/{id}`
- `POST /api/v1/admin/pricelist/reorder`
- `GET/PATCH /api/v1/admin/site-settings`
- `GET /api/v1/admin/scrape-runs`
- `POST /api/v1/admin/scrape-runs` (manual run, rate-limited)

Return consistent problem-details errors, OpenAPI schemas, pagination metadata, validation messages safe for users, and correlation IDs.

## 6. Design System & UI

**Component Library**: Angular Material (customized theme)  
**Visual direction**: Elegant, restrained, editorial, generous whitespace, warm neutrals, charcoal text, one muted metallic/accent color, fine borders, and high-quality image cropping. Avoid excessive animation and visual clutter.  
**Typography**: Use a refined, logo-compatible display treatment with a highly legible sans-serif body font; self-host or use a properly licensed provider. Final font selection should be validated against the supplied black-and-white logo.
**Layout**: Mobile-first responsive grid, max-width content container, sticky/compact header, prominent but calm calls to action, and consistent vertical rhythm.  
**Accessibility**: Visible focus rings, skip link, semantic headings, reduced-motion support, appropriate `alt` handling for the logo/map, empty `alt` attributes for gallery images where no descriptive text is provided, keyboard-operable dialogs/forms, and adequate contrast.
**Component Library Defaults**: Angular Material components for buttons, navigation, cards, tables, dialogs, snackbars, form fields, menus, progress indicators, and responsive sidenav; use CSS for brand-specific composition rather than raw repeated controls.

### Frontend routes and components

- `/`: `HomePage` with hero, value proposition, featured services, gallery teaser, booking CTA.
- `/pricelist`: `PricelistPage`, category sections, service duration/price, Square booking link.
- `/gallery`: `GalleryPage`, responsive image grid/lightbox, pagination and empty/error states.
- `/contact`: `ContactPage`, details, hours, social/booking links, accessible map image and attribution.
- `/pricelist`: a direct link to the studio's Square services and booking page.

Shared components: `SiteHeader`, `SiteFooter`, `BookingButton`, `LoadingState`, `ErrorState`, `ConfirmDialog`, `ImageLightbox`, `AuthGuard`, `UnsavedChangesGuard`, and API/interceptor services.

## 7. Security, Privacy & Operational Risks

- Keep database and scraper credentials in a root-readable Droplet secrets file outside the repository, with GitHub Actions protected-environment secrets limited to deployment. No secrets may appear in the repository, Docker layers, logs, or frontend bundles. Do not expose PostgreSQL directly to the public internet.
- Instagram scraping can violate Instagram terms, robots expectations, rate limits, or account rules; obtain owner/legal approval, use public data only by default, throttle, cache, identify the user agent, provide a kill switch, and be prepared to replace it with an approved feed/API.
- Scraped media/captions and the map image may have copyright/privacy restrictions. Store only approved media, preserve attribution where required, obtain map-image license/attribution, and support takedown/deletion.
- Square content may change; do not scrape it in production without permission. Treat manual entry/import as the source of truth and link to Square for booking.
- Defend image and thumbnail processing against oversized files, malformed content, SSRF, path traversal, decompression bombs, and unbounded disk usage; enforce MIME, duration, and size limits, generate thumbnails in an isolated worker, and malware-scan if uploads are later added.

## 8. Testing & Quality Plan

- Backend unit tests for gallery access, readiness, scraper deduplication, retry/backoff, and migration behavior.
- API integration tests with disposable PostgreSQL and a temporary local media directory; contract tests generated from OpenAPI.
- Angular unit/component tests and Playwright end-to-end tests for public navigation, Square booking links, gallery loading, and error states.
- Worker tests with mocked Instagram responses, multi-image carousel fixtures, video-thumbnail fixtures, rate-limit/error scenarios, idempotent reruns, the 1,000-asset limit, and retention cleanup.
- Accessibility checks with axe/Playwright; responsive smoke tests at mobile/tablet/desktop breakpoints.
- CI security scans for dependencies, containers, secrets, and static analysis; backup/restore and migration rehearsal before production.

## 9. Local Development & Delivery

### Local development

Provide `docker-compose.yml` for PostgreSQL, a persistent local media volume, API, worker, and optional frontend dev proxy. Include `.env.example` containing placeholders only, Make/PowerShell-friendly commands, Alembic migration commands, seed-free bootstrap-admin command, and documented test commands. Angular uses `ng serve`; FastAPI uses Uvicorn reload; worker supports a one-shot local scrape against fixtures/mock mode and video-thumbnail generation.

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

1. **Recommended**: DigitalOcean Droplet running Docker Compose + Managed PostgreSQL + persistent local media + GitHub Actions, with Cloudflare DNS/proxy for `jewelessencehairstudio.co.uk`. This supports the API, frontend, and scheduled worker on one controlled host without introducing a separate media service.
2. **Alternative**: A separate Droplet for the worker or frontend if resource usage, isolation, or availability requirements grow. This adds cost and operational complexity but reduces contention between workloads.
3. **Portable**: Any Docker host with managed PostgreSQL/object storage and cron. Lowest DigitalOcean coupling, but more responsibility for deployment, TLS, secrets, backups, and monitoring.

### Milestones

1. Confirm remaining assumptions, legal approval for Instagram/map, production option, and initial admin phone/bootstrap process; import the supplied logo and map assets.
2. Scaffold repository structure and Docker Compose; create migrations and API contract.
3. Implement API/auth/admin and Angular public/admin routes.
4. Implement gallery storage, worker, retention, and audit/status UI.
5. Apply visual polish, accessibility, tests, security hardening, and performance budgets.
6. Harden the Droplet, configure Docker Compose and scheduled worker execution, set up GitHub Actions deployment, Cloudflare DNS/HTTPS/custom-domain routing, backups/monitoring, owner acceptance, and production release.

### Definition of ready for scaffold

This plan is implementation-ready once the user confirms the remaining decisions in Section 3 and explicitly approves this plan. The next agent must read this file and scaffold only after approval; it must not silently introduce a contact form, live Square integration, Instagram credentials, email-based authentication, or unsupported identity provider.
