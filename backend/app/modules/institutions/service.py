from fastapi import HTTPException
from ..auth.guards import obligation_scope
from ...core.errors import object_id
from . import repository
from .schemas import InstitutionView, InstitutionPage


def scope(db, user):
    allowed = obligation_scope(user)
    if user['role'] == 'committee':
        return {'_id': {'$in': repository.assigned_institutions(db, allowed)}}
    if user['role'] == 'institution':
        return {'_id': allowed['institution_id']}
    return allowed


def view(row):
    return InstitutionView(id=row['_id'], name=row['name'], region=row['region'],
                           is_new=row['is_new'], version=row['version'])


def get(db, user, identifier):
    oid = object_id(identifier)
    rows, _ = repository.page(db, {'$and': [scope(db, user), {'_id': oid}]}, 1, 0)
    if not rows:
        raise HTTPException(404, 'Institution not found')
    return view(rows[0])


def page(db, user, limit, offset):
    rows, total = repository.page(db, scope(db, user), limit, offset)
    return InstitutionPage(items=[view(row) for row in rows], total=total, limit=limit, offset=offset)
