"""Application assembly only. Run separately from preserved backend.main:app."""
from contextlib import asynccontextmanager
from uuid import uuid4
import json
import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
from .core.settings import Settings
from .db.lifecycle import connect, initialize
from .api.router import router
from .engine.clock import DemoClock, RealClock


def create_app(settings=None):
    settings = settings or Settings()
    request_log = logging.getLogger('clockwork.requests')
    request_log.setLevel(logging.INFO)
    request_log.propagate = False
    if not request_log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        request_log.addHandler(handler)

    @asynccontextmanager
    async def lifespan(app):
        client = connect(settings)
        app.state.db = client[settings.mongo_database]
        app.state.clock = DemoClock(app.state.db) if settings.mode == 'demo' else RealClock()
        app.state.initialized = False
        try:
            await run_in_threadpool(initialize, app.state.db)
            app.state.initialized = True
        except (PyMongoError, RuntimeError):
            # Liveness remains available; restart after fixing DB/index setup.
            request_log.warning(json.dumps({'event': 'database_startup_unavailable'}))
        yield
        client.close()

    app = FastAPI(title='ClockWork API', version='1.0.0', lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                       allow_credentials=True, allow_methods=['GET', 'POST'],
                       allow_headers=['X-ClockWork-CSRF', 'Content-Type'])

    @app.middleware('http')
    async def request_context(request, call_next):
        request.state.correlation_id = str(uuid4())
        if request.url.path.startswith('/api/v1/') and '/health/' not in request.url.path and not app.state.initialized:
            response = JSONResponse({'error': {'code': 503, 'message': 'Database not ready',
                                               'correlation_id': request.state.correlation_id}}, status_code=503)
        else:
            response = await call_next(request)
        response.headers['X-Correlation-ID'] = request.state.correlation_id
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        # Deliberately omit URL/query/body/headers/cookies and exception text.
        request_log.info(json.dumps({
            'event': 'http', 'method': request.method, 'status': response.status_code,
            'correlation_id': request.state.correlation_id}))
        return response

    async def error(request, exc):
        status = exc.status_code if isinstance(exc, StarletteHTTPException) else 422 if isinstance(exc, RequestValidationError) else 503
        message = exc.detail if isinstance(exc, StarletteHTTPException) else 'Invalid request' if status == 422 else 'Operation unavailable'
        return JSONResponse({'error': {'code': status, 'message': message,
                                       'correlation_id': request.state.correlation_id}}, status_code=status)

    for kind in (StarletteHTTPException, RequestValidationError, PyMongoError, RuntimeError):
        app.add_exception_handler(kind, error)
    app.include_router(router)
    return app


app = create_app()
