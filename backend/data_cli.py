"""Run with python -m backend.data_cli init|seed|inspect [--db PATH]."""
import argparse
import json
import sqlite3
from contextlib import closing

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func, text

from .database import database_path, database_target, engine_for, initialize
from .seed import BUNDLE_PATH, seed
from .models import MODELS, DemoClock, User, Application


def inspect_postgres(engine):
    with engine.connect() as connection, connection.begin():
        connection.execute(text('SET TRANSACTION READ ONLY'))
        return {
            'counts': {m.__tablename__: connection.scalar(select(func.count()).select_from(m)) for m in MODELS},
            'demo_clock': connection.scalar(select(DemoClock.now_at)).isoformat(),
            'users': [dict(r) for r in connection.execute(select(
                User.username, User.role, User.region, User.institution_id, User.committee).order_by(User.id)).mappings()],
            'applications': [dict(r) for r in connection.execute(select(
                Application.id, Application.institution_id, Application.current_stage, Application.status).order_by(Application.id)).mappings()],
        }


def inspect_data(path):
    """Read-only connection and explicit columns: never display password hashes."""
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as con:
        con.execute('PRAGMA query_only=ON')
        return {
            'counts': {m.__tablename__: con.execute(f'SELECT COUNT(*) FROM {m.__tablename__}').fetchone()[0] for m in MODELS},
            'demo_clock': con.execute('SELECT now_at FROM demo_clock WHERE id=1').fetchone()[0],
            'regions': con.execute('SELECT region, COUNT(*) FROM institutions GROUP BY region').fetchall(),
            'roles': con.execute('SELECT role, COUNT(*) FROM users GROUP BY role').fetchall(),
            'users': con.execute('SELECT username, role, region, institution_id, committee FROM users ORDER BY id').fetchall(),
            'applications': con.execute('SELECT id, institution_id, current_stage, status FROM applications ORDER BY id').fetchall(),
            'foreign_key_violations': con.execute('PRAGMA foreign_key_check').fetchall(),
            'warning': 'Synthetic demonstration. Login and processing workflow are implemented; scheduling, uploads and delivery remain pending.',
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init','seed','inspect'])
    parser.add_argument('--db', help='Absolute path or path relative to the project root')
    parser.add_argument('--data', default=str(BUNDLE_PATH), help='Canonical synthetic JSON bundle (seed only)')
    args = parser.parse_args()
    target = database_target(args.db)
    remote = '://' in target
    path = None if remote else database_path(target)
    engine = None
    try:
        if args.command == 'inspect':
            if remote:
                engine = engine_for(target)
                result = inspect_postgres(engine)
            else:
                result = inspect_data(path)
        else:
            engine = engine_for(target)
            if args.command == 'seed':
                with open(args.data, encoding='utf-8') as stream:
                    result = seed(engine, json.load(stream))
            else:
                initialize(engine)
                result = {'initialized': True}
        print(json.dumps({'database': 'PostgreSQL / private clockwork schema' if remote else str(path), **result}, indent=2))
    except (ValueError, KeyError, OSError, sqlite3.Error, SQLAlchemyError) as exc:
        message = type(exc).__name__ if remote else str(exc)
        parser.exit(1, f'Rejected: {message}\nNo existing rows were overwritten.\n')
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    main()
