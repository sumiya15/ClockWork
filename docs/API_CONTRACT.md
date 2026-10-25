# Phase 1 API contract

Canonical schemas: FastAPI `/openapi.json` and `/docs`, new entry point
`backend.app.main:app` on 8002. Application routes use `/api/v1`.

| Method / path | Access / behavior |
|---|---|
| GET /health/live | Public; process liveness |
| GET /health/ready | Public; writable replica-set primary and successful startup indexes |
| GET /health/scheduler | Public; explicitly disabled in Phase 1 |
| POST /auth/login | JSON username/password, Origin + X-ClockWork-CSRF: 1; sets HttpOnly cookie; returns safe user + expiry |
| GET /auth/me | Cookie session; safe current identity |
| POST /auth/logout | Cookie + CSRF; revokes server session, clears cookie |
| GET /institutions | Role-scoped page, limit 1–100, offset >=0 |
| GET /institutions/{id} | Scoped record; malformed ID 422, inaccessible/missing 404 |
| GET /obligations | Scoped page; kind/state allowlist, limit/offset, stable saved due/ID ordering |
| GET /obligations/{id} | Scoped computed obligation view |
| GET /rules | Admin only; at most 100 published rule versions, read-only |

Paths in the table are relative to `/api/v1`. OpenAPI describes cookie security.
No write route for obligation/case/clock/rule mutation is exposed in this phase.
Admin rule validation/preview/publication must be implemented before exposing edits.

Page response: `{items,total,limit,offset}`, with `business_at` for obligations.
Each obligation exposes stored lifecycle/evidence state, rule/version, active/baseline
due and separately computed `days_remaining`/`deadline_severity`. No client identity
or arbitrary Mongo query dictionary is accepted. Unknown list filters fail with 422.

Login/logout return 409 if account identity, role or scope changes between the
initial read and transaction snapshot. Retry the request. No session/audit mutation
or cookie change commits on that conflict; a failed logout is not successful revocation.

Errors: `{error:{code,message,correlation_id}}`; no submitted passwords, raw body,
database URI or exception trace is returned. 401 unauthenticated/expired; 403 scope
or CSRF denied; 404 concealed inaccessible resource; 409 concurrent account change;
422 invalid input; 503 database
or atomic operation unavailable. Correlation IDs are server-generated response headers.
Responses disable caching. Startup index errors keep liveness available and readiness
false; fix database configuration and restart. Startup never seeds business records.

Browser requests use same-origin `/api` through the Vite dev proxy. For a separately
hosted client set VITE_API_BASE_URL and an exact CW_ALLOWED_ORIGINS JSON array; use
the same site with HTTPS for Strict cookies. Never expose Mongo credentials in VITE_ values.

## Standalone frontend mode
Default frontend demo mode calls no API. Hash routes include case/<id>, registers/<id>, upload/<register-id>, rules and notifications. These are browser views, not new REST endpoints. The simulated upload route is not a secure magic-link API. Existing /api/v1 contracts remain unchanged; select VITE_APP_MODE=api to use them.

