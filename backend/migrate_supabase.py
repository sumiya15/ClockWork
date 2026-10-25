"""Copy a schema-3 SQLite snapshot to an empty private Supabase schema."""
import argparse
import json
import os

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import URL

from .database import POSTGRES_SCHEMA, create_postgres_tables, database_path, engine_for
from .models import Base, SchemaInfo


def read_snapshot(path):
    # SQLite URI mode=ro prevents accidental source creation or writes.
    source = create_engine(URL.create('sqlite', database='file:' + path.as_posix(),
                                     query={'mode': 'ro', 'uri': 'true'}))
    try:
        with source.connect() as connection:
            connection.exec_driver_sql('BEGIN')
            if set(inspect(connection).get_table_names()) != set(Base.metadata.tables):
                raise ValueError('Source must have the complete ClockWork schema')
            if connection.execute(select(SchemaInfo.version).where(SchemaInfo.id == 1)).scalar() != 3:
                raise ValueError('Initialize the SQLite source to schema 3 before migration')
            if connection.exec_driver_sql('PRAGMA foreign_key_check').all():
                raise ValueError('Source has foreign-key violations')
            return {table.name: [dict(row) for row in connection.execute(select(table)).mappings()]
                    for table in Base.metadata.sorted_tables}
    finally:
        source.dispose()


def copy_snapshot(snapshot, target):
    if target.dialect.name != 'postgresql':
        raise ValueError('Destination must be Supabase PostgreSQL')
    with target.begin() as connection:
        connection.execute(text('SELECT pg_advisory_xact_lock(1129008971)'))
        if inspect(connection).get_table_names(schema=POSTGRES_SCHEMA):
            raise ValueError('Destination clockwork schema must be empty; no rows were overwritten')
        create_postgres_tables(connection)
        for table in Base.metadata.sorted_tables:
            rows = snapshot[table.name]
            if rows:
                connection.execute(table.insert(), rows)
            saved = [dict(row) for row in connection.execute(select(table)).mappings()]
            key = lambda row: tuple(str(row[column.name]) for column in table.primary_key)
            if sorted(saved, key=key) != sorted(rows, key=key):
                raise ValueError(f'Copy verification failed for {table.name}; transaction rolled back')
        return {name: len(rows) for name, rows in snapshot.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='data/clockwork.sqlite3')
    args = parser.parse_args()
    target = None
    try:
        url = os.environ.get('CLOCKWORK_DATABASE_URL')
        if not url:
            raise ValueError('Set CLOCKWORK_DATABASE_URL locally before migrating')
        snapshot = read_snapshot(database_path(args.source))
        target = engine_for(url)
        counts = copy_snapshot(snapshot, target)
        print(json.dumps({'copied_and_verified': counts, 'schema': POSTGRES_SCHEMA}, indent=2))
    except Exception as exc:
        # Driver exceptions can include SQL parameters containing hashes/tokens.
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        parser.exit(1, f'Migration not completed: {message}. Source unchanged.\n')
    finally:
        if target is not None:
            target.dispose()


if __name__ == '__main__':
    main()
