"""Deny-by-default SQL scopes shared by lists, detail lookups and nested routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import false, func, select, true
from sqlalchemy.orm import Session

from .auth import current_user, get_db
from .models import Application, Institution, Obligation
from .schemas import ApplicationView, InstitutionView, ObligationView, Page

router = APIRouter(prefix='/api', tags=['Scoped synthetic reads'])


def app_scope(user):
    if user.role in {'bureau_officer', 'administrator'}:
        return true()
    if user.role == 'regional_officer' and user.region and user.region.strip():
        return Application.institution_id.in_(select(Institution.id).where(Institution.region == user.region))
    if user.role == 'institution' and user.institution_id and user.institution_id.strip():
        return Application.institution_id == user.institution_id
    if user.role == 'committee' and user.committee and user.committee.strip():
        # Assignment is the persisted task owner, never every case at an institution.
        return Application.id.in_(select(Obligation.application_id).where(Obligation.owner_user_id == user.id))
    return false()


def institution_scope(user):
    if user.role in {'bureau_officer', 'administrator'}:
        return true()
    if user.role == 'regional_officer' and user.region and user.region.strip():
        return Institution.region == user.region
    if user.role == 'institution' and user.institution_id and user.institution_id.strip():
        return Institution.id == user.institution_id
    if user.role == 'committee' and user.committee and user.committee.strip():
        return Institution.id.in_(select(Application.institution_id).where(app_scope(user)))
    return false()


def obligation_scope(user):
    result = Obligation.application_id.in_(select(Application.id).where(app_scope(user)))
    return result & (Obligation.owner_user_id == user.id) if user.role == 'committee' else result


def reject_unknown(request, allowed):
    if set(request.query_params) - set(allowed):
        raise HTTPException(422, 'Unsupported query parameter')


def require_record(db, model, record_id, scope):
    record = db.scalar(select(model).where(model.id == record_id, scope))
    if record is None:
        raise HTTPException(404, 'Record not found')
    return record


def page(db, query, model, limit, offset):
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    return {'items': db.scalars(query.order_by(model.id).limit(limit).offset(offset)).all(),
            'total': total, 'limit': limit, 'offset': offset}


@router.get('/institutions', response_model=Page[InstitutionView])
def institutions(request: Request, region: str | None = None,
                 limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
                 user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request, {'region','limit','offset'})
    query = select(Institution).where(institution_scope(user))
    if region is not None:
        query = query.where(Institution.region == region)
    return page(db, query, Institution, limit, offset)


@router.get('/institutions/{institution_id}', response_model=InstitutionView)
def institution(institution_id: str, request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request, set())
    return require_record(db, Institution, institution_id, institution_scope(user))


@router.get('/applications', response_model=Page[ApplicationView])
@router.get('/institutions/{institution_id}/applications', response_model=Page[ApplicationView])
def applications(request: Request, institution_id: str | None = None, region: str | None = None,
                 stage: str | None = None, status: str | None = None,
                 limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
                 user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request, {'institution_id','region','stage','status','limit','offset'} -
                   ({'institution_id'} if request.path_params else set()))
    if request.path_params:
        require_record(db, Institution, institution_id, institution_scope(user))
    query = select(Application).where(app_scope(user))
    if institution_id is not None:
        query = query.where(Application.institution_id == institution_id)
    if region is not None:
        query = query.where(Application.institution_id.in_(select(Institution.id).where(Institution.region == region)))
    if stage is not None:
        query = query.where(Application.current_stage == stage)
    if status is not None:
        query = query.where(Application.status == status)
    return page(db, query, Application, limit, offset)


@router.get('/applications/{application_id}', response_model=ApplicationView)
def application(application_id: str, request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request, set())
    return require_record(db, Application, application_id, app_scope(user))


@router.get('/obligations', response_model=Page[ObligationView])
@router.get('/applications/{application_id}/obligations', response_model=Page[ObligationView])
def obligations(request: Request, application_id: str | None = None, institution_id: str | None = None,
                status: str | None = None, owner_user_id: str | None = None,
                limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
                user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request, {'application_id','institution_id','status','owner_user_id','limit','offset'} -
                   ({'application_id'} if request.path_params else set()))
    if request.path_params:
        require_record(db, Application, application_id, app_scope(user))
    query = select(Obligation).where(obligation_scope(user))
    if application_id is not None:
        query = query.where(Obligation.application_id == application_id)
    if institution_id is not None:
        query = query.where(Obligation.application_id.in_(select(Application.id).where(Application.institution_id == institution_id)))
    if status is not None:
        query = query.where(Obligation.status == status)
    if owner_user_id is not None:
        query = query.where(Obligation.owner_user_id == owner_user_id)
    return page(db, query, Obligation, limit, offset)
