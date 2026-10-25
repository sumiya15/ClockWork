from fastapi import APIRouter, Depends, HTTPException, Query, Request
from ..auth.guards import current_user
from . import service
from .schemas import InstitutionView, InstitutionPage

router = APIRouter(prefix='/api/v1/institutions', tags=['Institutions'])


@router.get('', response_model=InstitutionPage)
def institutions(request: Request, limit: int = Query(20, ge=1, le=100),
                 offset: int = Query(0, ge=0), user=Depends(current_user)):
    if set(request.query_params) - {'limit', 'offset'}:
        raise HTTPException(422, 'Unknown query parameter')
    return service.page(request.app.state.db, user, limit, offset)


@router.get('/{institution_id}', response_model=InstitutionView)
def institution(institution_id: str, request: Request, user=Depends(current_user)):
    return service.get(request.app.state.db, user, institution_id)
