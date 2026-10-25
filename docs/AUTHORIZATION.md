# Authorization and browser security

Phase 1 read matrix (server enforced):

| Role | Operational obligations/institutions | Published rules | Processing/decisions |
|---|---|---|---|
| institution | Own institution only | Denied | No Phase 1 mutation endpoints |
| regional_officer | Assigned Region only | Denied | Future assigned-owner actions only |
| committee | Matching committee AND explicitly assigned user/case obligations; only associated institution summaries | Denied | Future assigned committee actions |
| bureau_officer | All-Region oversight reads | Denied | Oversight is not statutory approval |
| admin | Denied operational browsing | Allowed | No statutory authority from admin role |

Legacy SQL administrator behavior differs (oversight reads); it remains isolated
until an explicit migration. For Mongo, missing Region/institution/committee scope
fails closed. Scopes are reloaded from DB on every request, never accepted from a
role selector, header, request body or local state. List filters only narrow scope.
Later exports/downloads must reuse equivalent guards and explicit action permissions.

Passwords use pwdlib recommended Argon2, individually salted. Development accounts
are distinct and only explicitly seeded in isolated demo/test DBs. Public demo
passwords are not production authentication. User provisioning, login rate limiting,
password recovery and MFA are not implemented; keep the demo on loopback.

Sessions use 256-bit random opaque tokens, only SHA-256 digests in Mongo. The browser
gets a host-only HttpOnly, SameSite=Strict cookie restricted to /api/v1; Secure is
mandatory in real mode. No localStorage/sessionStorage token and no token in JSON.
Expiry is 60 minutes by default (configurable 1–480), checked by the application on
every request; Mongo TTL is only cleanup. There is no refresh token/sliding renewal:
expiry requires login again. Login rotates the browser's previous session; logout
revokes it transactionally and clears the cookie. Other devices remain logged in.

Login and logout both require exact allowed Origin, application/json, custom
X-ClockWork-CSRF: 1 and non-cross-site Fetch Metadata. Restricted CORS allows only
configured origins/headers with credentials. A hostile site cannot set this custom
header without passing preflight. SameSite alone is not the CSRF defense.

Audit failure prevents successful login/logout; clients must not claim logout
succeeded when the server fails. Passwords/tokens/bodies/query strings are omitted
from structured application request logs. Run Uvicorn with --no-access-log to avoid
raw query paths. Future magic links must be exchanged without token logging, with
HTTPS, no-referrer, no third-party content, scoped single/bounded use and retry-safe
file completion. No magic-link, upload, download or evidence-verification endpoints
are implemented in this phase.

Login/logout bind audit identity to the transaction's re-read user. If account ID,
role, institution, Region or committee changed since the initial read, the transaction
returns 409 with no session/audit/cookie change. Retry against fresh permissions.
This prevents a successful session mutation carrying stale audit attribution.

## Presentation persona simulation
Five local personas restrict demo views/actions/exports through shared selectors and mutation checks. They are not authentication or backend protection; the browser controls all data. Admin has no local workflow/verification action, and EVC committee actions require explicit assignment. Focused reminder URLs are public local simulations. The complete simulated matrix and limitations are in FRONTEND_DEMO.md. Backend authorization is unchanged.

