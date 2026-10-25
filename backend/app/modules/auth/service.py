import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from pwdlib import PasswordHash
from ...db.transactions import mutate
from . import repository
from .schemas import LoginView, public_user

passwords = PasswordHash.recommended()
DUMMY_HASH = passwords.hash(secrets.token_urlsafe(32))


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def authenticate(db, token, session=None):
    if not token or len(token) != 43:
        raise HTTPException(401, 'Authentication required')
    user = repository.session_user(db, token_hash(token), session)
    if user is None:
        raise HTTPException(401, 'Authentication required')
    return user


def _require_same_audit_identity(expected, current):
    # Audit arguments were captured before the transaction. Bind them to the
    # identity re-read in its snapshot, including account replacement and scope.
    fields = ('_id', 'role', 'institution_id', 'region', 'committee_id')
    if any(expected.get(field) != current.get(field) for field in fields):
        raise HTTPException(409, 'Account permissions changed; retry the request')


def login(db, settings, body, correlation_id, old_token=None):
    user = repository.by_username(db, body.username)
    valid = passwords.verify(body.password.get_secret_value(), user['password_hash'] if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, 'Invalid username or password')
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.session_minutes)

    def operation(session):
        fresh = repository.by_username(db, body.username, session)
        if not fresh or fresh['password_hash'] != user['password_hash']:
            raise HTTPException(401, 'Authentication required')
        _require_same_audit_identity(user, fresh)
        if old_token and len(old_token) == 43:
            repository.revoke(db, token_hash(old_token), session)
        repository.insert_session(db, {'_id': token_hash(token), 'user_id': fresh['_id'],
                                      'expires_at': expires, 'created_at': now, 'revoked_at': None,
                                      'schema_version': 1}, session)
        return fresh

    fresh = mutate(db, actor=str(user['_id']), institution=str(user['institution_id']) if user.get('institution_id') else None,
                   action='auth.login', resource='session', correlation_id=correlation_id, operation=operation,
                   role=user['role'], scope={'region': user.get('region'), 'committee_id': user.get('committee_id')})
    return LoginView(expires_at=expires, user=public_user(fresh)), token


def logout(db, token, correlation_id):
    user = authenticate(db, token)
    def operation(session):
        fresh = authenticate(db, token, session)
        _require_same_audit_identity(user, fresh)
        repository.revoke(db, token_hash(token), session)
    mutate(db, actor=str(user['_id']), institution=str(user['institution_id']) if user.get('institution_id') else None,
           action='auth.logout', resource='session', correlation_id=correlation_id, operation=operation, role=user['role'],
           scope={'region': user.get('region'), 'committee_id': user.get('committee_id')})
