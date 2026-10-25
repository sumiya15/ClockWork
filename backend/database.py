"""Explicit initialization only; importing the API never resets or seeds a DB."""
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

from .models import AuthSession, Base, DemoClock, SchemaInfo, WORKFLOW_MODELS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "backend/config/demo_rules.json"
POSTGRES_SCHEMA = 'clockwork'


def database_target(path=None):
    # Explicit file targets keep isolated tests independent of deployment settings.
    if path is not None:
        return str(path)
    return os.environ.get('CLOCKWORK_DATABASE_URL') or str(database_path())


def postgres_url(value):
    url = make_url(value)
    if url.drivername not in {'postgres', 'postgresql', 'postgresql+psycopg'}:
        raise ValueError('CLOCKWORK_DATABASE_URL must be a PostgreSQL connection URL')
    if url.query.get('sslmode', 'require') not in {'require', 'verify-ca', 'verify-full'}:
        raise ValueError('PostgreSQL connections require TLS')
    return url.set(drivername='postgresql+psycopg').update_query_dict(
        {'sslmode': url.query.get('sslmode', 'require')})


def write_lock(session):
    if session.bind.dialect.name == 'sqlite':
        session.connection().exec_driver_sql('BEGIN IMMEDIATE')
    else:
        # Transaction-scoped lock preserves existing check/insert and replay semantics.
        session.execute(text('SELECT pg_advisory_xact_lock(1129008971)'))


def database_path(path=None):
    value = Path(path or os.environ.get("CLOCKWORK_DB_PATH", "data/clockwork.sqlite3"))
    return (PROJECT_ROOT / value).resolve() if not value.is_absolute() else value.resolve()


def engine_for(path=None):
    target = database_target(path)
    if '://' in target:
        return create_engine(postgres_url(target), pool_pre_ping=True,
                             connect_args={'connect_timeout': 15, 'prepare_threshold': None},
                             execution_options={'schema_translate_map': {None: POSTGRES_SCHEMA}})
    path = target
    path = database_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(URL.create("sqlite", database=str(path)), connect_args={"timeout": 15})

    @event.listens_for(engine, "connect")
    def enforce_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    return engine


def initialize(engine):
    if engine.dialect.name == 'postgresql':
        with engine.begin() as connection:
            connection.execute(text('SELECT pg_advisory_xact_lock(1129008971)'))
            tables = set(inspect(connection).get_table_names(schema=POSTGRES_SCHEMA))
            if tables:
                if tables != set(Base.metadata.tables):
                    raise ValueError('Existing clockwork schema differs; explicit migration required')
                version = connection.execute(select(SchemaInfo.version).where(SchemaInfo.id == 1)).scalar()
                if version != 3:
                    raise ValueError('Unsupported PostgreSQL application schema')
                return
            create_postgres_tables(connection)
            config = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
            connection.execute(SchemaInfo.__table__.insert().values(id=1, version=3))
            connection.execute(DemoClock.__table__.insert().values(id=1, now_at=config['initial_demo_time']))
        return
    tables = set(inspect(engine).get_table_names())
    if tables:
        if SchemaInfo.__tablename__ not in tables:
            raise ValueError("Refusing an unrelated/reference database; choose a new application DB path")
        with Session(engine) as session:
            marker = session.get(SchemaInfo, 1)
            if marker is None or marker.version not in (1, 2, 3):
                raise ValueError("Unsupported application schema; explicit migration required")
            version = marker.version
        if version == 1:
            if tables != set(Base.metadata.tables) - {'auth_sessions'} - {m.__tablename__ for m in WORKFLOW_MODELS}:
                raise ValueError("Unexpected version 1 schema; migration refused")
            # Back up using SQLite's consistent online backup API before migration.
            path = Path(engine.url.database)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = path.with_name(f'{path.stem}.pre-auth-{stamp}.sqlite3')
            with closing(sqlite3.connect(path)) as source, closing(sqlite3.connect(backup)) as target:
                source.backup(target)
            with engine.connect() as connection:
                connection.exec_driver_sql('BEGIN IMMEDIATE')
                try:
                    AuthSession.__table__.create(connection, checkfirst=True)
                    connection.execute(SchemaInfo.__table__.update().where(SchemaInfo.id == 1).values(version=2))
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            tables.add('auth_sessions')
            version = 2
        if version == 2:
            if tables != set(Base.metadata.tables) - {m.__tablename__ for m in WORKFLOW_MODELS}:
                raise ValueError('Unexpected version 2 schema; workflow migration refused')
            path = Path(engine.url.database)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = path.with_name(f'{path.stem}.pre-workflow-{stamp}.sqlite3')
            with closing(sqlite3.connect(path)) as source, closing(sqlite3.connect(backup)) as target:
                source.backup(target)
            with engine.connect() as connection:
                connection.exec_driver_sql('BEGIN IMMEDIATE')
                try:
                    for model in WORKFLOW_MODELS:
                        model.__table__.create(connection)
                    connection.execute(SchemaInfo.__table__.update().where(SchemaInfo.id == 1).values(version=3))
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
            tables.update(m.__tablename__ for m in WORKFLOW_MODELS)
        if tables != set(Base.metadata.tables):
            raise ValueError("Incomplete or changed schema; explicit migration required")
        return
    Base.metadata.create_all(engine)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    with Session(engine) as session, session.begin():
        session.add(SchemaInfo(id=1, version=3))
        session.add(DemoClock(id=1, now_at=config["initial_demo_time"]))


def demo_now(session):
    """Future deadline code can use saved simulation time, never the OS clock."""
    value = session.scalar(select(DemoClock.now_at).where(DemoClock.id == 1))
    if value is None:
        raise ValueError("Demo clock has not been initialized")
    return value


def create_postgres_tables(connection):
    """Private backend schema; never expose password/session tables via Data API."""
    connection.execute(text('CREATE SCHEMA IF NOT EXISTS clockwork'))
    connection.execute(text('REVOKE ALL ON SCHEMA clockwork FROM PUBLIC'))
    Base.metadata.create_all(connection)
    for role in ('anon', 'authenticated'):
        if connection.execute(text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role': role}).scalar():
            connection.execute(text(f'REVOKE ALL ON SCHEMA clockwork FROM {role}'))
            connection.execute(text(f'REVOKE ALL ON ALL TABLES IN SCHEMA clockwork FROM {role}'))
    for table in Base.metadata.sorted_tables:
        name = connection.dialect.identifier_preparer.quote(table.name)
        connection.execute(text(f'ALTER TABLE clockwork.{name} ENABLE ROW LEVEL SECURITY'))
