"""Cookie sessions and origin/custom-header CSRF protection for the local API."""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import hashlib
import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import database_target, engine_for
from .models import AuthSession, User
from .passwords import hash_password, verify_password
from .schemas import LoginInput, LogoutView, UserView

router = APIRouter(prefix='/api/auth', tags=['Authentication'])
COOKIE = 'clockwork_session'
SESSION_SECONDS = 8 * 60 * 60
# Unknown usernames still perform the same password hash work.
DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def real_now():
    return datetime.now(timezone.utc)


def token_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


@lru_cache(maxsize=4)
def cached_engine(path):
    return engine_for(path)


def get_db():
    with Session(cached_engine(database_target())) as session:
        yield session


def allowed_origins():
    return {v.strip() for v in os.environ.get('CLOCKWORK_ALLOWED_ORIGINS',
            'http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8001,http://localhost:8001').split(',') if v.strip()}


def secure_cookie():
    return os.environ.get('CLOCKWORK_COOKIE_SECURE', 'false').lower() == 'true'


def csrf_guard(request: Request):
    """No CORS grants: browsers cannot send this custom header cross-origin.

    Also require an exact configured Origin, including for non-browser callers.
    This deliberately rejects missing/null origins and protects login CSRF too.
    """
    if (request.headers.get('origin') not in allowed_origins()
            or request.headers.get('x-clockwork-csrf') != '1'
            or request.headers.get('sec-fetch-site') == 'cross-site'
            or request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json'):
        raise HTTPException(403, 'Origin/CSRF check failed')


def authenticated_session(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE)
    if not token or len(token) != 43:
        raise HTTPException(401, 'Authentication required')
    session = db.get(AuthSession, token_digest(token))
    if session is None or session.revoked_at is not None or session.expires_at <= real_now():
        raise HTTPException(401, 'Authentication required')
    user = db.get(User, session.user_id)
    if user is None:
        raise HTTPException(401, 'Authentication required')
    return session, user


def current_user(auth=Depends(authenticated_session)):
    # Reloaded from the database on every request; no role/scope in the cookie.
    return auth[1]


@router.post('/login', response_model=UserView, dependencies=[Depends(csrf_guard)])
def login(body: LoginInput, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    valid = verify_password(body.password, user.password_hash if user else DUMMY_HASH)
    if user is None or not valid:
        raise HTTPException(401, 'Invalid username or password')
    now = real_now()
    old_token = request.cookies.get(COOKIE)
    if old_token:
        old = db.get(AuthSession, token_digest(old_token))
        if old is not None:
            old.revoked_at = now
    token = secrets.token_urlsafe(32)
    expires = now + timedelta(seconds=SESSION_SECONDS)
    db.add(AuthSession(token_hash=token_digest(token), user_id=user.id,
                       created_at=now, expires_at=expires))
    db.commit()
    response.set_cookie(COOKIE, token, max_age=SESSION_SECONDS, expires=expires,
                        httponly=True, secure=secure_cookie(), samesite='strict', path='/api')
    return user


@router.post('/logout', response_model=LogoutView, dependencies=[Depends(csrf_guard)])
def logout(response: Response, auth=Depends(authenticated_session), db: Session = Depends(get_db)):
    auth[0].revoked_at = real_now()
    db.commit()
    response.delete_cookie(COOKIE, path='/api', httponly=True, secure=secure_cookie(), samesite='strict')
    return {'status': 'logged_out'}


@router.get('/me', response_model=UserView)
def me(user=Depends(current_user)):
    return user
