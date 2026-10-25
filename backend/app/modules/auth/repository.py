from datetime import datetime, timezone


def by_username(db, username, session=None):
    return db.users.find_one({'username': username, 'active': True}, session=session)


def session_user(db, token_hash, session=None):
    login = db.sessions.find_one({'_id': token_hash, 'revoked_at': None,
                                 'expires_at': {'$gt': datetime.now(timezone.utc)}}, session=session)
    return db.users.find_one({'_id': login['user_id'], 'active': True}, session=session) if login else None


def insert_session(db, record, session):
    db.sessions.insert_one(record, session=session)


def revoke(db, token_hash, session):
    db.sessions.update_one({'_id': token_hash}, {'$set': {'revoked_at': datetime.now(timezone.utc)}}, session=session)
