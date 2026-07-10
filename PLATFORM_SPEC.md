> **Repo focus — gdg-babcock-hacktoberfest-2025 (FastAPI + Pillow certificate generator):** owns **§7 Certificates** — generalize the templates off Hacktoberfest branding (add ORBIT/GDG-generic or per-event templates), and secure the generator (currently open) so the auth service can call it on check-in to auto-issue "attended" certificates.
>
> _Shared cross-repo architecture spec — committed to every GDG Babcock platform repo so each can be built in parallel. Your repo's primary sections are flagged above; the full plan spans all services._

# GDG Babcock Platform — Events, Certificates, Profiles & Cross-Service Analytics (Architecture Spec)

**This round is a SPEC ONLY — no code is written.** It is a full architecture + roadmap across all repos, so the whole shape can be reviewed before any build begins. Decisions locked with the user: events data lives in the **auth (Postgres) service** reusing **ORBIT**'s registration patterns; the **RADAR identity + scoring foundation is in scope**; an **admin dashboard is in scope and also migrates team/member profiles off hardcoding**.

---

## 1. Context — why this, and the reality on the ground

The vision (stated in `GDGWebsite/README.md`) is a single identity that "follows a member across RADAR, Wrapped, Orbit, event attendance, and automatic certificates." Today that vision is **UI-complete but data-empty**: the profile page already renders tiles for *Events attended, Certificates, RADAR articles read, Reading minutes* — all showing `"—"` because no service writes them yet. The `/events` route doesn't exist (it's static homepage marketing copy). We want to make events **native** to the site (Luma-style: browse → register → check-in → shareable page), auto-issue **attendance certificates** on check-in, surface real **per-member stats** on profiles (events + RADAR games/reads), and expose **cross-service analytics** (top scorer, most-played game, aggregates) — plus an **admin dashboard** to run events and manage profiles instead of editing TypeScript.

**The three hard truths this spec must design around (from exploration):**

1. **The auth service is the source of truth, and it's Postgres — not Firestore.** `auth/` (Express 5 + `firebase-admin` for token verification only) holds all user data in Postgres. It has `users` (with `roles TEXT[]` already supporting `admin/moderator/lead`) and a ready-but-unused `requireRole()` guard — but **no events, attendance, certificate, or activity tables.** Every new data model in this spec lands here.
2. **RADAR has no users, no auth, and its games produce no scores.** `radar/` (Next.js + Sanity) has zero auth deps. Its two "games" (a hardcoded crossword, a personality quiz) persist nothing server-side — the crossword saves letters to `localStorage`, the quiz saves nothing. "Articles read" is only an **anonymous Redis view counter** (`views:<slug>` → int), not per-user. So "high scores / most-played / articles read per member" **cannot be read from anything today** — the identity + scoring substrate must be built first.
3. **The certificate generator already exists and is reusable.** `gdg-babcock-hacktoberfest-2025/backend/` is a **FastAPI + Pillow** service that overlays `name / event / date` onto a template PNG. It has `POST /certificates/` (+ bulk + CSV), stores rows in SQLite, and is currently **unauthenticated** with **Hacktoberfest-specific templates**. Reusable for "attended → certificate" via its `participation` template; needs generalizing + securing.

**Reference repos in the ecosystem** (all cloned under `/home/user`): `GDGWebsite` (Next.js 14 main site), `auth` (Express/Postgres SSO), `radar` (Next.js/Sanity), `gdgbabcockapplication` (static v0 recruitment microsite — *not* an event system, low relevance), `gdg-babcock-hacktoberfest-2025` (certificate generator). **`gdgbabcockuniversity/orbit`** (the existing ORBIT registration system) is **not yet in this session** — see §11; its exact schema/flows are the reconciliation target for the events model.

---

## 2. Target architecture (one identity, one hub)

```
                        ┌──────────────────────────────────────────┐
                        │   auth service  (Express + Postgres)      │
                        │   ── THE HUB / source of truth ──         │
   Firebase ID token ──▶│  users, roles[]  (existing)               │
                        │  events, event_registrations,             │
                        │  event_checkins, certificates  (NEW)      │
                        │  radar_game_scores, radar_reads (NEW)     │
                        │  activity views + analytics endpoints     │
                        └───────┬───────────────┬──────────────┬────┘
      platform JWT (existing)   │               │ in-proc/HTTP │ JWT
                                │               ▼              │
     ┌──────────────┐   ┌───────▼────────┐  ┌──────────────┐  │
     │ GDGWebsite   │   │ cert service   │  │ RADAR        │──┘
     │ /events      │   │ (FastAPI+Pillow│  │ +auth (NEW)  │
     │ /profile     │   │  generalized)  │  │ score hooks  │
     │ /admin (NEW) │   └────────────────┘  │ in games(NEW)│
     └──────────────┘                       └──────────────┘
```

**Principles**
- **Auth service owns all persistent cross-service data.** Every service authenticates the *same* platform JWT (issuer `auth-service`, audience `platform-services`) and writes/reads through auth-service endpoints. No second identity store.
- **Frontends stay thin:** the website mirrors its existing `lib/auth-service.ts` fetch+JWT+refresh pattern for a new `lib/events-service.ts` etc. The profile's existing placeholder contract (`lib/member.ts`) is the integration seam — it lights up when `/auth/me` returns `activity` + `certificates`.
- **Certificate service is a downstream renderer**, invoked by the auth service on check-in (HTTP `POST /certificates/`, or in-process if co-located), storing the resulting `unique_id`/URL back on the auth-side `certificates` row.

---

## 3. Data model — new Postgres tables in `auth/database/schema.sql`

All FK → `users(id)`; follow existing conventions (UUID PKs via `gen_random_uuid()`, `updated_at` trigger, soft-delete where sensible). **Reconcile column names/enums against the ORBIT repo's registration schema before finalizing (§11).**

```sql
-- Events (admin-authored)
events (
  id UUID PK, slug TEXT UNIQUE, title TEXT, description TEXT,
  cover_image_url TEXT, location TEXT, is_online BOOLEAN,
  starts_at TIMESTAMPTZ, ends_at TIMESTAMPTZ,
  registration_opens_at TIMESTAMPTZ, registration_closes_at TIMESTAMPTZ,
  capacity INT NULL, track TEXT NULL, program TEXT NULL,   -- ORBIT / Meetup / GDG Week / Babcock100
  certificate_type TEXT DEFAULT 'participation',           -- feeds cert service
  status TEXT DEFAULT 'draft',                             -- draft|published|ended|cancelled
  visibility TEXT DEFAULT 'public',
  created_by UUID FK users, created_at, updated_at )

-- Registration (RSVP) — one per (event,user)
event_registrations (
  id UUID PK, event_id FK events, user_id FK users,
  status TEXT DEFAULT 'registered',                        -- registered|waitlisted|cancelled
  registered_at TIMESTAMPTZ, UNIQUE(event_id, user_id) )

-- Check-in — the attendance record that triggers a certificate
event_checkins (
  id UUID PK, event_id FK events, user_id FK users,
  checked_in_at TIMESTAMPTZ, checked_in_by UUID FK users, -- admin/self via QR
  method TEXT,                                             -- qr|manual|self
  UNIQUE(event_id, user_id) )

-- Certificates — issued on check-in, links to cert-service artifact
certificates (
  id UUID PK, user_id FK users, event_id FK events NULL,
  title TEXT, cert_service_unique_id TEXT, download_url TEXT,
  issued_at TIMESTAMPTZ, is_shareable BOOLEAN DEFAULT TRUE )

-- RADAR per-user activity (see §8 for how it gets written)
radar_game_scores (
  id UUID PK, user_id FK users, game TEXT,                 -- 'crossword'|'quiz'|...
  puzzle_id TEXT, score INT, meta JSONB, played_at TIMESTAMPTZ )
radar_reads (
  id UUID PK, user_id FK users, slug TEXT, seconds INT,
  read_at TIMESTAMPTZ, UNIQUE(user_id, slug) )            -- upsert; sum seconds → minutes
```

**Derived `activity` for the profile** (matches `MemberActivity` in `GDGWebsite/lib/member.ts` exactly, so the UI needs no shape changes): `events_attended` = count of `event_checkins`; `radar_articles_read` = count of `radar_reads`; `radar_reading_minutes` = `sum(seconds)/60`; `stars`/`streak` = later gamification. Expose as a computed sub-object on `GET /auth/me` (and a dedicated `GET /users/:id/activity`).

---

## 4. API surface — new endpoints in `auth/src` (routes/controllers/services/models)

Mirror the existing controller/service/model layering. Gate writes with the existing `authenticateToken`; gate admin actions with the existing (currently unused) `requireRole(['admin'])`.

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/events` | public | List published events (filters: upcoming/past, program). |
| GET | `/events/:slug` | public | Event detail (+ counts). Powers shareable page + OG tags. |
| POST | `/events` / PUT `/events/:id` | admin | Create/update (admin dashboard). |
| POST | `/events/:id/register` | user | RSVP (capacity/waitlist logic). |
| DELETE | `/events/:id/register` | user | Cancel RSVP. |
| POST | `/events/:id/checkin` | admin/self | Mark attendance → **triggers certificate issuance** → inserts `certificates` row. |
| GET | `/events/:id/attendees` | admin | Roster + check-in state (dashboard). |
| GET | `/auth/me` (extend) | user | Add computed `activity` + `certificates[]`. |
| GET | `/users/:id/activity` | user/admin | Stats for a profile. |
| GET | `/analytics/overview` | admin | Cross-service aggregates (§9). |
| POST | `/radar/scores` | user | Record a game score (from RADAR). |
| POST | `/radar/reads` | user | Record an article read (from RADAR). |
| Admin user/profile mgmt | `/admin/users*` | admin | List/edit users, set `roles`, manage team roster (§10). |

---

## 5. Events on the website — `GDGWebsite/` (Next.js 14 App Router)

- **New routes:** `app/events/page.tsx` (browse: upcoming/past), `app/events/[slug]/page.tsx` (detail + Register/Cancel + shareable). Add **OpenGraph/Twitter meta** via route `generateMetadata` so an event link unfurls with cover + title/date ("shareable event").
- **New data layer:** `lib/events-service.ts` — copy the fetch+JWT+refresh+`authHeaders()` pattern straight from `lib/auth-service.ts` (401 → refresh → retry). Add TS types (`PlatformEvent`, `Registration`).
- **Replace static events:** `components/sections/annual-structure.tsx` (`#events`) currently hardcodes 4 `PHASES`. Add a real "Upcoming events" section fed by `/events` (keep the annual-rhythm framing as the evergreen backdrop; slot live events above it).
- **Nav:** add `/events` to `components/navigation.tsx` (already conditionally shows `/profile` + Sign In via `useAuth()`).
- **Check-in UX:** self-check-in via a per-event QR that deep-links to `app/events/[slug]?checkin=<token>`; admins check people in from the dashboard (§10). QR carries a signed short-lived token, not a raw user id.

## 6. Profile — `GDGWebsite/app/profile/page.tsx` (mostly already built)

The Activity tiles + Certificates section already exist and read through `lib/member.ts` `getActivity()` / `getCertificates()`, which optional-cast off the user record. **Wiring = backend-only:** once `/auth/me` returns `activity` + `certificates[]`, extend `PlatformUser` in `lib/auth-service.ts` with those fields and the tiles/cards light up automatically. Add the Bevy-style breakdown: *events registered vs attended vs checked-in*, and a "Certificates" grid with per-cert share links (each cert `download_url` from the cert service; `is_shareable`). RADAR game stats (high scores, most-played) render here too once §8 lands.

## 7. Certificates — generalize `gdg-babcock-hacktoberfest-2025/backend/`

- **Generalize templates:** the generator hardcodes Hacktoberfest templates + Figma coordinates (`services/generator.py`, `certificate_type ∈ {participation, completion}`). Add a neutral/ORBIT/GDG-generic template (or per-event template selection) so "attended ORBIT 2026" renders on-brand. Input contract is fixed & clean (`models/certificates.py`): `participant_name` (letters/space/hyphen/apostrophe only), `event_name`, `date_issued` (YYYY-MM-DD), `certificate_type` — auth service supplies `full_name` from `users`, event title, ISO date, `participation`.
- **Secure it:** currently open (CORS `*`, no token). Require a service token / platform JWT before it can be called from the check-in flow.
- **Trigger:** on `POST /events/:id/checkin`, auth service calls the cert service (`POST /certificates/`, or in-process import if co-located), then stores `unique_id` + `download_url` on the auth `certificates` row → surfaces on the profile.

## 8. RADAR foundation — `radar/` (the biggest net-new workstream)

RADAR must gain identity + persistence it has never had:
- **Shared auth:** add Firebase client sign-in + platform-JWT exchange to RADAR, reusing the exact pattern from `GDGWebsite/components/auth-provider.tsx` + `lib/auth-service.ts` (Firebase ID token → `POST /auth/login` → JWT in storage). RADAR then knows the same `users.id`.
- **Score hooks in the games:** emit a score event where each game currently resolves — `app/components/CrosswordPuzzle.tsx` at its `isComplete` memo (score from correctness/time), `app/components/PersonalityQuiz.tsx` at its tally/result. Each fires `POST /radar/scores` `{ game, puzzle_id, score, meta }` with the JWT. (Requires giving the games an actual numeric score — today they have none; define scoring rules per game.)
- **Reads:** keep the anonymous Redis counter for public totals, but *additionally* fire `POST /radar/reads` `{ slug, seconds }` from `app/components/ViewCounter.tsx` when a user is signed in, so per-member reads/minutes exist.
- **Result:** the profile's `radar_articles_read` / `radar_reading_minutes` and game high-scores become real; leaderboards/analytics (§9) have data.

## 9. Cross-service analytics dashboard — `GDGWebsite/app/admin/analytics` + `/analytics/overview`

Admin-only aggregates over the new tables: **top scorer** (`max/sum score` per user over `radar_game_scores`), **most-played game** (count by `game`), most-read articles, event attendance funnels (registered→attended), per-track participation. Build the API as SQL aggregate queries in the auth service; render with the site's existing dataviz conventions. (Everything here depends on §8 data existing first — it's the *last* thing to light up.)

## 10. Admin dashboard + migrating profiles off hardcoding — `GDGWebsite/app/admin/*`

- **Gate:** `app/admin/layout.tsx` guards on `user.roles?.includes('admin')` (role already on `PlatformUser`); non-admins 404/redirect. Add an `isAdmin` convenience to `auth-provider.tsx`.
- **Event ops:** create/edit events, view attendee roster, **check people in** (search + QR scan), issue/re-issue certs, see per-event stats. This is the minimum to actually *run* an event.
- **Profile/roster migration:** today the team roster is hardcoded in `GDGWebsite/lib/team-data.ts` and member profiles live in the auth `users` table but aren't linked to team cards. Plan:
  1. Add admin `/admin/users` to list/search users, edit fields, and set `roles`/`teams` (backed by new `/admin/users*` endpoints — the self-serve `PUT /auth/profile` deliberately strips `roles`, so admin role-setting is net-new).
  2. Model the **team roster in Postgres** (either a `team_positions` table linking `users.id` → role/section/subteam/year, or promote the org fields onto users) so `app/team/page.tsx` reads live data instead of `team-data.ts`. Link team cards to platform profiles via school email (the `docs/team-form-fields.md` field #15 "link later" hook).
  3. Provide a one-time importer from the current `team-data.ts` + `member-seed-data.ts` into the new tables, then retire the hardcoded files.

---

## 11. ORBIT repo — reconcile before building the events model

The user confirmed a **`gdgbabcockuniversity/orbit`** repo holds the registration system actually used for ORBIT. It is **not in this session yet** (the `add_repo`/`list_repos` calls need an approval that plan mode blocks). Before the "Events" phase is implemented, **add and read that repo** to reconcile: exact registration fields, waitlist/capacity rules, check-in mechanism (QR format?), and any attendee data worth importing — then align the §3 tables/§4 endpoints to it rather than diverging. If its name differs from `gdgbabcockuniversity/orbit`, confirm it.

---

## 12. Phased roadmap (build order when we leave spec mode)

- **Phase 0 — foundation:** add ORBIT repo + reconcile schema (§11); land the `events/registrations/checkins/certificates` tables + migrations in auth; wire the existing `requireRole` for admin gating.
- **Phase 1 — events end-to-end:** auth event/register/checkin endpoints → website `/events` browse+detail+register (shareable OG) → admin event CRUD + check-in → certificate issuance on check-in (generalize + secure cert service) → profile "events attended" + certificates light up.
- **Phase 2 — RADAR foundation:** RADAR auth + score hooks in games + per-user reads → profile RADAR stats real.
- **Phase 3 — analytics + full admin/profile migration:** cross-service `/analytics/overview` dashboard; migrate team roster + profiles off hardcoding with admin management UI.

## 13. Open decisions / risks to settle at build time
- **Cert service hosting / language boundary:** auth is Node, cert generator is Python — simplest is an authenticated HTTP call from auth → the FastAPI service (vs co-locating). Decide before Phase 1.
- **Game scoring rules:** crossword & quiz have no scores today; define what "score" means per game before §8.
- **QR/self-check-in security:** signed short-lived tokens, not raw user ids; anti-abuse (one check-in per user/event enforced by `UNIQUE`).
- **PII:** attendee rosters + matric numbers are sensitive — admin-only, audit via existing `auth_audit_log`.
- **RADAR framework drift:** RADAR is Next 16/React 19 vs website Next 14/React 18 — auth wiring must be ported, not shared as a package (or extract a tiny shared auth client).

## 14. Verification approach (per phase, when built — not this round)
- **Auth service:** migrations apply cleanly; endpoint tests for register/checkin/cert-issue happy-path + auth/role rejection; check-in idempotency (`UNIQUE`).
- **Website:** `pnpm exec tsc --noEmit` (build skips type errors) + drive the real flow — sign in → register → admin check-in → certificate appears on profile → event link unfurls (OG). Playwright for the shareable page + profile tiles.
- **RADAR:** sign in → complete a game → score persists → shows on profile; per-user read increments minutes.
- **Analytics:** aggregates match seeded fixtures (top scorer / most-played).

---

**Deliverable status:** This document is the requested spec — no repository code has been changed this round. The immediate real-world next action when we move to build is Phase 0: **add `gdgbabcockuniversity/orbit` and reconcile the events schema against it.**
