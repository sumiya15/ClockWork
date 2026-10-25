from fastapi import APIRouter, Depends, Request
from ..auth.guards import current_user, require_admin
from ...engine.rules import RuleSet
from .service import published

router = APIRouter(prefix='/api/v1/rules', tags=['Rules'])


@router.get('', response_model=list[RuleSet])
def rules(request: Request, user=Depends(current_user)):
    require_admin(user)
    return published(request.app.state.db)
