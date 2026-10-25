"""ClockWork student demonstration: backend foundation only."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .auth import router as auth_router
from .read_api import router as read_router
from .workflow import router as workflow_router

app = FastAPI(
    title="ClockWork API",
    version="0.1.0",
    description=(
        "Student demonstration in demo mode. Login and scoped read APIs use a "
        "local synthetic database. Filing, processing-stage completion, return and resubmission "
        "are implemented. Scheduling, uploads and AICTE integration are not implemented. "
        "Example timelines and access scopes are proposed "
        "demonstration settings pending validation against official rules."
    ),
)

app.include_router(auth_router)
app.include_router(read_router)
app.include_router(workflow_router)


@app.middleware('http')
async def private_response_headers(request, call_next):
    spoof_headers = {'x-role', 'x-user-id', 'x-region', 'x-institution-id', 'x-committee'}
    if request.url.path.startswith('/api/') and spoof_headers.intersection(request.headers):
        response = JSONResponse({'detail': 'Client identity/scope headers are not accepted'}, status_code=400)
    else:
        response = await call_next(request)
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Vary'] = 'Cookie'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Do not echo submitted passwords or arbitrary body values in validation errors.
    return JSONResponse({'detail': [{'loc': e['loc'], 'type': e['type'], 'msg': e['msg']}
                                    for e in exc.errors()]}, status_code=422)


@app.exception_handler(SQLAlchemyError)
async def database_unavailable(request, exc):
    return JSONResponse({'detail': 'Database unavailable; initialize the application database'}, status_code=503)


@app.get("/", summary="Student demonstration server status")
def read_root() -> dict[str, str | bool]:
    return {
        "project": "ClockWork",
        "message": "ClockWork API is running as a student demonstration.",
        "demo_mode": True,
    }


@app.get("/api/health", summary="Server liveness only")
def health() -> dict[str, str]:
    """Confirms the API responds; does not check a database or external services."""
    return {"status": "ok"}
