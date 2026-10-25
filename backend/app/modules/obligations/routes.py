from fastapi import APIRouter, Depends, HTTPException, Query, Request
from ..auth.guards import current_user
from .schemas import Kind, State, ObligationPage, ObligationView
from . import service

router = APIRouter(prefix='/api/v1/obligations', tags=['Obligations'])


@router.get('', response_model=ObligationPage)
def obligations(request: Request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                kind: Kind | None = None, state: State | None = None, user=Depends(current_user)):
    if set(request.query_params) - {'limit', 'offset', 'kind', 'state'}:
        raise HTTPException(422, 'Unknown query parameter')
    filters = {k: v for k, v in {'kind': kind, 'state': state}.items() if v is not None}
    app = request.app.state
    return service.page(app.db, user, app.clock, app.settings, filters, limit, offset)


@router.get('/{obligation_id}', response_model=ObligationView)
def obligation(obligation_id: str, request: Request, user=Depends(current_user)):
    app = request.app.state
    return service.get(app.db, user, app.clock, app.settings, obligation_id)
