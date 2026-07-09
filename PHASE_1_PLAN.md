> **Repo focus — gdg-babcock-hacktoberfest-2025 (FastAPI + Pillow certificate generator):** your workstream is **C** — add a `require_service_token` bearer-secret dependency on the POST endpoints (GET download stays public), replace the wildcard CORS with an env-driven allowlist, and add an optional `template: "gdg"` option with fallback to the existing Hacktoberfest templates. Keep the `participant_name` regex unchanged (the auth service sanitizes on its side). C can proceed in parallel with the auth repo's A–B but must land before Workstream D's verification gate.
>
> _Shared Phase 1 implementation plan — committed to every repo Phase 1 touches. Your repo's workstream is flagged above; the full sequence spans all three services._

# Phase 1 Implementation Plan — GDG Babcock Platform: Events End-to-End

_Companion to `PLATFORM_SPEC.md` (§12 Phase 1 + its Phase 0 prerequisites). Written for the implementing agent: follow the workstreams **in order**, do not skip verification gates, and obey the Gotchas list at the bottom. Each workstream depends on the previous ones as sequenced._

## Scope

**IN:** Events tables + endpoints in the auth service; cert-service securing + auth→cert integration on check-in; `/auth/me` activity + certificates; website events browse/detail pages with OG metadata; nav + homepage upcoming-events; minimal admin dashboard (event CRUD, roster, check-in); profile type extension.

**OUT (do not build, do not scaffold):** RADAR ingestion/auth (Phase 2), analytics dashboards (Phase 3), team-roster migration (Phase 3), waitlist mechanics (schema supports the status value only; behavior = reject when full), orbit ticket data import, QR self-check-in (stretch step at the very end only — skip if anything else is incomplete).

**ORBIT reconciliation (spec §11) — resolved:** the `orbit` repo was reviewed. It is a one-off Firestore SPA for a single conference (tickets keyed by email: `fullName, email, role, checkedIn`, department/level captured at check-in; no capacity enforcement, no QR, no timestamps, no certificates). Nothing architectural to copy — the spec §3 schema stands as designed. Importing orbit ticket data is out of scope.

## Locked decisions (do not revisit)

1. **Cert integration:** auth calls the FastAPI service over HTTPS with a shared bearer secret. Auth env: `CERT_SERVICE_URL`, `CERT_SERVICE_TOKEN`. FastAPI env: `CERT_SERVICE_TOKEN`, checked by a dependency on `POST /certificates/` only (GET download stays public). Cert issuance is **non-blocking**: check-in commits first; a `certificates` row is created with `status='pending'` inside the check-in transaction; issuance runs after commit in try/catch; failure leaves the row `pending`/`failed`. Re-POSTing check-in for the same user is idempotent and retries any non-`issued` certificate — that IS the retry mechanism; build nothing fancier.
2. **QR self-check-in:** deferred to the stretch step at the end. Admin dashboard check-in is the Phase 1 MVP.
3. **Slugs:** server-side `slugify(title)` (lowercase, non-alphanumeric→`-`, collapse/trim dashes); on UNIQUE collision append `-2`, `-3`, … **Capacity:** enforced by a `COUNT(*)` of `status='registered'` rows inside the registration transaction; when full, respond 409 — do not waitlist.
4. **Name sanitization:** done on the **auth side** before calling the cert service (Workstream D). Do **not** relax the FastAPI `participant_name` regex (it would break the service's existing tests).

## Git workflow rules (mandatory)

- Commit after **each workstream** completes (not one giant commit) and push immediately (`git push -u origin <branch>`) so progress is never wiped.
- Author every commit **solely** as `nekumartins <akpotohwoo@gmail.com>` (use `git -c user.name=nekumartins -c user.email=akpotohwoo@gmail.com commit ...`).
- **No** `Co-Authored-By` trailers, no AI-tool signatures or identity of any kind in commit messages, code comments, or docs.

---

## Workstream A — auth: database schema

### A1. Create `auth/database/migrations/002_events.sql` (new file; do NOT append to `schema.sql`)

Rationale: `database/schema.sql` is applied manually with `psql -f` and contains a non-idempotent `CREATE TRIGGER update_users_updated_at` at line 116 — re-applying the whole file errors. New DDL goes in a separate additive file. Every statement must be idempotent (`IF NOT EXISTS` / `DROP TRIGGER IF EXISTS` before `CREATE TRIGGER`).

Contents (match existing conventions: `gen_random_uuid()` UUID PKs, `TIMESTAMP WITH TIME ZONE`, `idx_<table>_<col>` names, reuse the existing `update_updated_at_column()` function — do not redefine it):

```sql
-- events
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  cover_image_url TEXT,
  location TEXT,
  starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
  ends_at TIMESTAMP WITH TIME ZONE,
  capacity INTEGER,                       -- NULL = unlimited
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','published','ended','cancelled')),
  certificate_type TEXT NOT NULL DEFAULT 'participation'
    CHECK (certificate_type IN ('participation','completion')),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- event_registrations
CREATE TABLE IF NOT EXISTS event_registrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'registered'
    CHECK (status IN ('registered','waitlisted','cancelled')),
  registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (event_id, user_id)
);

-- event_checkins
CREATE TABLE IF NOT EXISTS event_checkins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  checked_in_by UUID REFERENCES users(id) ON DELETE SET NULL,
  checked_in_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (event_id, user_id)
);

-- certificates
CREATE TABLE IF NOT EXISTS certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_id UUID REFERENCES events(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  cert_service_unique_id TEXT,
  download_url TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','issued','failed')),
  issued_at TIMESTAMP WITH TIME ZONE,
  is_shareable BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_events_slug ON events(slug);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_starts_at ON events(starts_at);
CREATE INDEX IF NOT EXISTS idx_event_registrations_event_id ON event_registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_event_registrations_user_id ON event_registrations(user_id);
CREATE INDEX IF NOT EXISTS idx_event_checkins_event_id ON event_checkins(event_id);
CREATE INDEX IF NOT EXISTS idx_event_checkins_user_id ON event_checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_certificates_user_id ON certificates(user_id);

DROP TRIGGER IF EXISTS update_events_updated_at ON events;
CREATE TRIGGER update_events_updated_at
  BEFORE UPDATE ON events
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

Note: `certificates.status` is an addition beyond the spec's §3 sketch — it is required for the fault-tolerant issuance design (locked decision 1).

**Verification gate A:** `psql "$DATABASE_URL" -f database/migrations/002_events.sql` succeeds; run it a **second time** to prove idempotency; then `psql "$DATABASE_URL" -c "\d events"` shows the columns above.

---

## Workstream B — auth: events endpoints

Follow the existing layering exactly: route → controller → service → model, static-method ES6 classes, **CommonJS** (`require`/`module.exports` — never `import`).

### B1. `auth/src/models/eventModel.js` (new)

`EventModel` static methods (all use `query`/`transaction` from `../config/database`; `transaction()` exists at `src/config/database.js:52` and is currently unused — this is where it gets used):

- `create(data)` / `update(id, data)` / `findById(id)` / `findBySlug(slug)`
- `list({ status, upcoming })` — default `status='published'`; each row includes `registered_count` via subquery `(SELECT COUNT(*) FROM event_registrations r WHERE r.event_id = e.id AND r.status='registered')`.
- `register(eventId, userId)` — **inside `transaction()`**: `SELECT ... FROM events WHERE id=$1 FOR UPDATE`; reject if status ≠ `'published'` (409); if `capacity IS NOT NULL`, `SELECT COUNT(*)` of registered rows and reject 409 "Event is full" if count ≥ capacity; then `INSERT ... ON CONFLICT (event_id, user_id) DO UPDATE SET status='registered', registered_at=CURRENT_TIMESTAMP WHERE event_registrations.status='cancelled'` (re-register after cancel; a live duplicate returns 0 rows → treat as 409 "Already registered").
- `cancelRegistration(eventId, userId)` — `UPDATE event_registrations SET status='cancelled' WHERE event_id=$1 AND user_id=$2 AND status='registered'`.
- `getRegistration(eventId, userId)`; `listAttendees(eventId)` — join `event_registrations` × `users` (id, full_name, email, matric_no, department), left-join `event_checkins` (checked_in_at), left-join `certificates` (status, download_url).
- `checkIn(eventId, userId, adminId, certTitle)` — **inside `transaction()`**: verify a `registered` registration exists (else error → 404); `INSERT INTO event_checkins ... ON CONFLICT (event_id,user_id) DO NOTHING`; `INSERT INTO certificates (user_id, event_id, title, status) VALUES ($1,$2,$3,'pending') ON CONFLICT (user_id, event_id) DO NOTHING`; then `SELECT` and return the certificate row so retries get the existing row.
- `markCertificateIssued(certId, uniqueId, downloadUrl)` / `markCertificateFailed(certId)`.

### B2. `auth/src/services/eventService.js` (new)

`EventService`: slugify + uniqueness loop (query `findBySlug`, append `-2`, `-3`…); input validation (title required, `starts_at` valid ISO date, capacity positive int or null, status/certificate_type in allowed sets); orchestrates check-in + cert issuance (calls `CertificateService` from Workstream D — until D lands, wrap a stub call in try/catch).

### B3. `auth/src/controllers/eventController.js` (new)

Thin `EventController` static handlers mapping service results to the existing response envelope `{ success: true, ... }` / `{ success: false, message }`. Attendee response objects must expose: `user_id, full_name, email, matric_no, department, registered_at, checked_in_at (nullable), certificate_status (nullable), certificate_url (nullable)`.

### B4. `auth/src/routes/eventRoutes.js` (new) + mount in `auth/app.js`

```js
const { authenticateToken, requireRole } = require("../middleware/authMiddleware");
router.get("/", EventController.list);                    // public, ?status=&upcoming=
router.get("/:slug", EventController.getBySlug);          // public (404 for non-published)
router.post("/", authenticateToken, requireRole(["admin"]), EventController.create);
router.put("/:id", authenticateToken, requireRole(["admin"]), EventController.update);
router.post("/:id/register", authenticateToken, EventController.register);
router.delete("/:id/register", authenticateToken, EventController.cancelRegistration);
router.post("/:id/checkin", authenticateToken, requireRole(["admin"]), EventController.checkIn); // body: { user_id }
router.get("/:id/attendees", authenticateToken, requireRole(["admin"]), EventController.attendees);
```

Notes: `requireRole` lives in `src/middleware/authMiddleware.js` but is unused today — **read its exact implementation before wiring** (argument shape, how it reads `req.user.roles`). Public `GET /:slug` returns 404 for anything not in `('published','ended')`; the admin UI reads drafts through `GET /events?status=draft` with an admin token (make `list` allow non-published statuses only when a valid admin token is present, otherwise force `published`). Mount in `app.js` next to the line-45 `/auth` mount: `app.use("/events", eventRoutes);`. Express 5 note: keep exactly one public GET-by-param route (`/:slug`) — do not add a separate public `GET /:id`.

**Verification gate B:** `node --check` each new file; start the server (`npm start` with a valid `DATABASE_URL`); curl matrix: (1) `GET /events` → `{ success:true, events: [] }`; (2) `POST /events` without token → 401, with non-admin token → 403, with admin token → 201 with slugged event (grant admin via SQL: `UPDATE users SET roles = array_append(roles,'admin') WHERE email='...'`); (3) register twice → second 409; (4) capacity=1 with two users → second 409; (5) `DELETE .../register` then re-`POST` → succeeds.

---

## Workstream C — cert service: secure it + generic template

Repo: `gdg-babcock-hacktoberfest-2025/backend` (FastAPI + Pillow, has pytest).

### C1. Auth dependency — edit `app/api/certificates.py` (and/or new `app/api/deps.py`)

New dependency `require_service_token`: read `Authorization: Bearer <token>`, compare with `secrets.compare_digest` against `os.environ["CERT_SERVICE_TOKEN"]`; 401 if missing/mismatched; 503 if the env var itself is unset (fail closed). Apply as `dependencies=[Depends(require_service_token)]` on **POST /certificates/** (and the bulk POST endpoints) only. `GET /certificates/{unique_id}` remains public (users download PNGs by direct link).

### C2. CORS — edit `app/main.py`

Replace `allow_origins=["*"]` (main.py:26) with an env-driven list: `ALLOWED_ORIGINS` comma-separated, default `"https://gdgbabcock.com,https://auth.gdgbabcock.com,http://localhost:3000"`. (With `allow_credentials=True`, `"*"` is invalid per the CORS spec anyway.)

### C3. Generic GDG template — edit `app/services/generator.py` + request model

- Add optional field `template: str = "hacktoberfest"` (allowed: `hacktoberfest`, `gdg`) to the POST request schema in `app/models/certificates.py`.
- Generator selects the template file by `(template, certificate_type)`: gdg → `templates/gdg_participation_template.png` / `templates/gdg_completion_template.png`. **Fallback:** if the gdg file does not exist on disk, fall back to the existing hacktoberfest template (do not 500). Polished PNG assets are out of scope — generate a simple placeholder with a one-off Pillow script (`scripts/make_gdg_template.py`), **same pixel dimensions as the existing templates** so the hardcoded text coordinates in `generator.py` still land correctly.
- Do **not** touch the `participant_name` regex.

**Verification gate C:** `cd backend && python -m pytest` — existing tests in `tests/test_certificates.py` will fail on 401 first; update them to send the bearer header (set `CERT_SERVICE_TOKEN` via monkeypatch/env in conftest). Add one test: POST without token → 401. All tests green.

---

## Workstream D — auth: check-in → certificate wiring

### D1. `auth/src/services/certificateService.js` (new)

`CertificateService.issue({ certId, participantName, eventTitle, certificateType })`:

1. **Sanitize name** to satisfy the cert-service regex `^[a-zA-Z\s\-'\.]+$` (2–100 chars): NFD-normalize and strip diacritics (`name.normalize("NFD").replace(/[\u0300-\u036f]/g, "")`), replace every remaining disallowed char with a space, collapse whitespace, trim, truncate to 100; if the result is shorter than 2 chars use `"GDG Member"`.
2. `fetch(`${CERT_SERVICE_URL}/certificates/`)` with method POST, headers `Authorization: Bearer ${CERT_SERVICE_TOKEN}` + `Content-Type: application/json`, body `{ participant_name, event_name: eventTitle, date_issued: <today YYYY-MM-DD>, certificate_type, template: "gdg" }`. Node 18+ global `fetch` — no new dependency. Timeout via `AbortSignal.timeout(10000)`.
3. On 2xx: `EventModel.markCertificateIssued(certId, resp.unique_id, absoluteDownloadUrl)` where `absoluteDownloadUrl = CERT_SERVICE_URL + resp.download_url` (the service returns a **relative** `/certificates/{unique_id}` — always store the absolute URL).
4. On any error: log and `markCertificateFailed(certId)` — **never throw out of this function**.

### D2. Wire into check-in in `eventService.js`

`checkIn` flow: run `EventModel.checkIn(...)` transaction → commit → then, if the returned certificate row status is `pending` or `failed`, `await CertificateService.issue(...)` inside try/catch. The check-in HTTP response is 200 regardless of cert outcome; include `certificate_status` in the response body. Idempotent retry: admin re-clicks "Check in" → the checkIn transaction no-ops on conflicts, returns the existing cert row, and issuance retries if not `issued`. Certificate `title` = `"Certificate of ${certificate_type === 'completion' ? 'Completion' : 'Participation'} — ${event.title}"`.

### D3. Env

Add `CERT_SERVICE_URL` (no trailing slash) and `CERT_SERVICE_TOKEN` to auth's env documentation (README / `.env.example` if present).

**Verification gate D:** run FastAPI locally (`uvicorn app.main:app --port 8000` with `CERT_SERVICE_TOKEN=devtoken`), auth with `CERT_SERVICE_URL=http://localhost:8000 CERT_SERVICE_TOKEN=devtoken`; check in a registered test user via curl → `success:true`; `psql` shows the certificates row `status='issued'` with `cert_service_unique_id` and an absolute `download_url`; opening the URL serves a PNG. Then **kill FastAPI** and check in a second user → check-in still 200, cert row stays `pending`; restart FastAPI, re-POST checkin → row becomes `issued`.

---

## Workstream E — auth: extend GET /auth/me

### E1. Edit `auth/src/controllers/authController.js` (`getCurrentUser`) and `auth/src/models/userModel.js`

The controller currently calls `UserModel.getProfile` directly (skips the service) — keep that pattern; add two model methods:

- `UserModel.getActivity(userId)` → `{ events_attended: <COUNT(*) FROM event_checkins WHERE user_id=$1> }`. Return integers, not strings — `parseInt(rows[0].count, 10)`; pg returns COUNT as a string. Do **not** fabricate `stars`/`streak`/`radar_*` — omit them; the profile UI renders "—" for absent keys.
- `UserModel.getCertificates(userId)` → rows from `certificates WHERE user_id=$1 AND status='issued' ORDER BY issued_at DESC`, **mapped on the auth side** to the exact shape the website's `lib/member.ts` reads: `{ id: row.id, title: row.title, event: <events.title via JOIN, nullable>, issued_at: row.issued_at, url: row.download_url }`. Field names must be exactly `id, title, event, issued_at, url`.

`getCurrentUser` response becomes `{ success: true, user: { ...existing 10 columns, activity: {...}, certificates: [...] } }` — nested **inside** `user`, because the website parses `data.user`.

**Verification gate E:** curl `GET /auth/me` with the checked-in test user's token → `user.activity.events_attended === 1` and `user.certificates[0]` has keys `id,title,event,issued_at,url` with an absolute `url`. Existing callers unaffected (additive fields only).

---

## Workstream F — website: events service + public pages

Repo: `GDGWebsite`. **pnpm** (never npm/yarn), strict TS, `@/*` alias, Tailwind v4 (config-less — no tailwind.config.js edits; theme lives in `app/globals.css`).

### F1. `GDGWebsite/lib/events-service.ts` (new)

- Types: `EventSummary { id, slug, title, description, cover_image_url?, location?, starts_at, ends_at?, capacity?, status, certificate_type, registered_count? }`; `EventAttendee { user_id, full_name, email, matric_no?, department?, registered_at, checked_in_at?, certificate_status?, certificate_url? }`.
- Base URL: reuse `AUTH_API_URL` from `lib/auth-service.ts` if exported; if module-private, duplicate the one-liner (`process.env.NEXT_PUBLIC_AUTH_API_URL || "https://auth.gdgbabcock.com"`) — do not refactor auth-service exports beyond what's needed.
- **Server-usable public fetchers** (no localStorage, safe in server components): `fetchPublishedEvents()` → `GET /events?status=published` with `{ next: { revalidate: 60 } }`; `fetchEventBySlug(slug)` → `GET /events/${slug}`, returns `null` on 404.
- **Client-only authed actions** (copy the exact pattern from `lib/auth-service.ts`: `authHeaders(token)`, on 401 → `refreshAccessToken()` → retry once; tokens from localStorage keys `gdg_access_token`/`gdg_refresh_token`): `registerForEvent(eventId)`, `cancelRegistration(eventId)`, `createEvent(payload)`, `updateEvent(id, payload)`, `fetchAttendees(eventId)`, `checkInAttendee(eventId, userId)`, `fetchAdminEvents()`. Use the same tolerant response parse (`data.events || data.data?.events || data.data || data`).

### F2. `GDGWebsite/app/events/page.tsx` (new — **server component**)

Async server component: `fetchPublishedEvents()`, partition into upcoming (`starts_at >= now`) and past, render cards (reuse existing card styling conventions, e.g. from `app/products/page.tsx`, and shadcn components) linking to `/events/${slug}`. `export const revalidate = 60`. Static `export const metadata` for the listing page (pattern: `title: "Events — GDG Babcock"`).

### F3. `GDGWebsite/app/events/[slug]/page.tsx` (new — server component, the repo's first dynamic route) + `GDGWebsite/components/events/register-button.tsx` (new — client island)

- Page: `async function EventPage({ params }: { params: { slug: string } })` — in Next 14 `params` is a plain object (not a Promise; that's Next 15 — do not `await` it). `fetchEventBySlug` → `notFound()` on null. Renders detail + `<RegisterButton eventId={...} capacityFull={...} />`.
- `export async function generateMetadata({ params })` — fetches the same event (Next fetch dedup makes the double call free) and returns `{ title, description, openGraph: { title, description, images: [cover_image_url], type: "article" } }`. This is the repo's **first** `generateMetadata` — there is no in-repo pattern to copy; use the standard Next 14 App Router signature.
- `RegisterButton`: `"use client"`, uses `useAuth()` from `components/auth-provider.tsx`; unauthenticated → route into the existing login flow; authenticated → Register / Cancel via `events-service` actions, optimistic label swap, toast on 409 ("Event is full" / "Already registered").

**Verification gate F:** `pnpm tsc --noEmit` clean; `pnpm build` succeeds (dynamic route compiles); `pnpm dev` with `NEXT_PUBLIC_AUTH_API_URL=http://localhost:<auth-port>` → `/events` lists the published test event; `/events/<slug>` renders; `curl -s localhost:3000/events/<slug> | grep og:` shows OG tags in the **server-rendered HTML** (if OG tags are missing, the page accidentally became a client component); register button works end-to-end while logged in.

---

## Workstream G — website: nav + homepage

### G1. Edit `GDGWebsite/lib/content/site.ts`

Add `{ label: "Events", href: "/events" }` to `NAV_LINKS` (this file is the source of truth — **not** `navigation.tsx`).

### G2. `GDGWebsite/components/sections/upcoming-events.tsx` (new, async server component) + edit `GDGWebsite/app/page.tsx`

New section component: `fetchPublishedEvents()`, filter to the next 3 upcoming, render compact cards + "View all events →" link; **return `null` when there are no upcoming events** (the homepage must not show an empty section). Render it in `app/page.tsx` immediately **above** `<AnnualStructure />` (the static PHASES section in `components/sections/annual-structure.tsx` — do not modify annual-structure itself). Confirm `app/page.tsx` is a server component (no `"use client"`); if it turns out to be client, keep `UpcomingEvents` as a server component composed from a parent — do not fetch with useEffect.

**Verification gate G:** `pnpm build`; homepage shows the upcoming event above PHASES; nav shows Events in desktop and mobile menus.

---

## Workstream H — website: minimal admin

All admin pages are **client components** (the JWT lives in localStorage — server components cannot see it).

### H1. `GDGWebsite/app/admin/layout.tsx` (new)

`"use client"`; `useAuth()`; while `loading` render a spinner; if `!isAuthenticated || !user?.roles?.includes("admin")` render an access-denied card (link home) — do not silently redirect (avoids loops during token refresh). Wrap children in a simple container with an "Admin" heading.

### H2. `GDGWebsite/app/admin/page.tsx` (new)

Event list (all statuses via `fetchAdminEvents`), table with title/status/starts_at/registered_count, "New event" opening a form (shadcn Dialog or inline): fields title, description, location, starts_at (datetime-local), ends_at, capacity, status select, certificate_type select, cover_image_url. Create → `createEvent`; Edit reuses the same form with `updateEvent`. Row links to `/admin/events/[id]`.

### H3. `GDGWebsite/app/admin/events/[id]/page.tsx` (new)

Attendee roster via `fetchAttendees(eventId)`: table of full_name / email / matric_no / registered_at / checked-in badge / certificate status; per-row "Check in" button → `checkInAttendee` → refetch roster. Button disabled once `checked_in_at` is set **and** the cert is `issued`; when checked in but cert is `pending`/`failed`, relabel it "Retry cert" (re-POSTing check-in retries issuance per Workstream D).

**Verification gate H:** `pnpm tsc --noEmit`, `pnpm build`; manual: non-admin sees access-denied at `/admin`; admin creates a draft event, publishes it, sees it on `/events`; a normal user registers in another browser profile; admin checks them in; roster shows an issued cert with a working download link.

---

## Workstream I — website: profile type extension

### I1. Edit `GDGWebsite/lib/auth-service.ts` — and nothing else

Extend `PlatformUser` (lines 11–37) with `activity?: MemberActivity;` and `certificates?: MemberCertificate[];` using **`import type { MemberActivity, MemberCertificate } from "@/lib/member"`** (type-only import avoids any runtime circular-import risk). **No changes to `app/profile/page.tsx`** — its Certificates grid (~line 739) and Activity tiles (~line 782) already read via `getActivity(user)`/`getCertificates(user)` and light up automatically once `/auth/me` returns the fields; the Workstream E shape matches `MemberCertificate { id, title, event?, issued_at?, url? }` exactly.

**Verification gate I:** `pnpm tsc --noEmit`; log in as the checked-in test user → profile shows Events attended = 1 and one certificate card whose link downloads the PNG.

---

## Workstream J — end-to-end verification checklist (run last, in full)

With auth (local, dev Postgres), FastAPI (local, `CERT_SERVICE_TOKEN` set), and the website (`pnpm dev`) all running:

1. `psql -f database/migrations/002_events.sql` twice — no errors.
2. Admin token: create event → slug auto-generated; create a second event with the same title → slug gets `-2`.
3. `GET /events` public shows only published; a draft event 404s at `GET /events/<draft-slug>`.
4. Website `/events` and `/events/[slug]` render; `curl | grep 'og:title'` finds OG meta.
5. User registers via the UI; a capacity-1 event rejects a second user with a visible toast.
6. Admin checks the user in via `/admin/events/[id]`; cert row `issued`; PNG downloads.
7. Kill FastAPI, check in another user → check-in succeeds, cert `pending`; restart, retry → `issued`.
8. `/auth/me` returns `user.activity.events_attended` and `user.certificates[]`; profile tiles light up.
9. `POST /certificates/` on FastAPI without bearer → 401; with token → 200. `python -m pytest` green.
10. `pnpm build` and `pnpm tsc --noEmit` clean; `node --check` on every new/edited auth JS file.
11. Name edge case: set a test user's `full_name` to `José Núñez-Ẹ̀mí, Jr.`, check in → cert issues (sanitizer worked).

## Stretch (Phase 1.5 — only if everything above is done): QR self-check-in

Auth: `GET /events/:id/checkin-token` (admin) returns a short-lived (10 min) JWT `{ event_id, purpose: "checkin" }` signed with `JWT_SECRET`; `POST /events/checkin/self` (authenticated user) verifies that token from the request body and runs the same `EventModel.checkIn` path with `checked_in_by = user_id`. Website: QR render (e.g. `qrcode.react`) on the admin roster page encoding `https://gdgbabcock.com/events/checkin?token=...`, plus a tiny client page at `app/events/checkin/page.tsx` that reads the token from searchParams and calls the self-check-in endpoint. Skip entirely if time-constrained.

## Gotchas — MUST NOT violate

1. **Non-idempotent trigger:** never re-run `database/schema.sql` against a live DB (the trigger at line 116 errors); all new DDL goes in `database/migrations/002_events.sql` with guarded triggers.
2. **auth is CommonJS:** `require`/`module.exports` only. No `import` statements, no `"type": "module"`.
3. **Cert name regex:** FastAPI rejects names outside `^[a-zA-Z\s\-'\.]+$` — always run the Workstream D sanitizer before calling it; do not change the regex.
4. **Vercel /tmp SQLite:** the cert service's SQLite DB and PNG files are ephemeral in production. Auth's `certificates` table stores `cert_service_unique_id` + `download_url` **and** everything needed to re-issue (user name, event title, type); the idempotent check-in retry is the recovery path. Build nothing that assumes the cert-service DB is durable.
5. **`expires_in` hardcode:** the auth stack hardcodes token expiry (86400 in the login response); do not "fix" or depend on it — copy the existing client 401→refresh→retry pattern verbatim.
6. **Tailwind v4 is config-less:** no `tailwind.config.js/ts` edits; theme tokens live in `app/globals.css`.
7. **pnpm, not npm** in GDGWebsite; plain `npm` in auth.
8. **Server/client split for OG:** `app/events/page.tsx` and `app/events/[slug]/page.tsx` must stay server components (no `"use client"`, no localStorage) or `generateMetadata` OG tags break; interactivity lives only in small client islands. Admin pages are the opposite: fully client, because tokens are in localStorage.
9. **`/auth/me` shape:** `activity` and `certificates` nest inside `user`; certificate keys are exactly `id, title, event, issued_at, url`; `download_url` must be stored/returned absolute; pg `COUNT` returns strings — parseInt before returning.
10. **`requireRole` is currently dead code** — read its implementation before wiring; don't assume its argument shape.
