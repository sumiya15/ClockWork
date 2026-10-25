from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyCookie
from .service import authenticate

COOKIE = 'clockwork_v1_session'
cookie = APIKeyCookie(name=COOKIE, auto_error=False)


def access_token(token: str | None = Depends(cookie)):
    return token


def current_user(request: Request, token=Depends(access_token)):
    return authenticate(request.app.state.db, token)


def csrf_guard(request: Request):
    if (request.headers.get('origin') not in request.app.state.settings.allowed_origins
            or request.headers.get('x-clockwork-csrf') != '1'
            or request.headers.get('content-type', '').split(';')[0] != 'application/json'
            or request.headers.get('sec-fetch-site') == 'cross-site'):
        raise HTTPException(403, 'Origin/CSRF check failed')


def obligation_scope(user):
    if user['role'] == 'institution' and user.get('institution_id'):
        return {'institution_id': user['institution_id']}
    if user['role'] == 'regional_officer' and user.get('region'):
        return {'region': user['region']}
    if user['role'] == 'committee' and user.get('committee_id'):
        return {'committee_id': user['committee_id'], 'owner_user_id': user['_id']}
    if user['role'] == 'bureau_officer':
        return {}
    raise HTTPException(403, 'Operational scope required')


def require_admin(user):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Administrator permission required')
