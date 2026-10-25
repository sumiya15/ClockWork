from fastapi import APIRouter, HTTPException, Request
from pymongo.errors import PyMongoError

router = APIRouter(prefix='/api/v1/health', tags=['Health'])


@router.get('/live')
def live() -> dict[str, str]:
    return {'status': 'alive'}


@router.get('/ready')
def ready(request: Request) -> dict[str, str]:
    try:
        hello = request.app.state.db.client.admin.command('hello')
        if not hello.get('isWritablePrimary') or not hello.get('setName') or not request.app.state.initialized:
            raise HTTPException(503, 'Database not ready')
    except PyMongoError:
        raise HTTPException(503, 'Database not ready') from None
    return {'status': 'ready'}


@router.get('/scheduler')
def scheduler() -> dict[str, str]:
    return {'status': 'disabled', 'reason': 'Deadline evaluator and worker are Phase 3; no jobs are being delivered'}
