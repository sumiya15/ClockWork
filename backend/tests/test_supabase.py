"""Offline compatibility checks; these do not claim a live Supabase connection."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from backend.database import database_target, engine_for, initialize, postgres_url, write_lock
from backend.migrate_supabase import read_snapshot, copy_snapshot
from backend.models import Base


class SupabaseConfigurationTests(unittest.TestCase):
    def test_url_selection_tls_and_explicit_test_database(self):
        url = 'postgresql://demo:secret@db.example.test/postgres'
        with patch.dict(os.environ, {'CLOCKWORK_DATABASE_URL': url}):
            self.assertEqual(database_target(), url)
            self.assertEqual(database_target('isolated.sqlite3'), 'isolated.sqlite3')
            engine = engine_for()
            try:
                self.assertEqual(engine.dialect.name, 'postgresql')
                self.assertEqual(engine.url.query['sslmode'], 'require')
                self.assertEqual(engine.get_execution_options()['schema_translate_map'], {None: 'clockwork'})
            finally:
                engine.dispose()
        for bad in ['sqlite:///wrong.db', url + '?sslmode=disable']:
            with self.assertRaises(ValueError):
                postgres_url(bad)

    def test_all_tables_compile_for_postgresql(self):
        for table in Base.metadata.sorted_tables:
            self.assertIn('CREATE TABLE', str(CreateTable(table).compile(dialect=postgresql.dialect())))

    def test_postgres_lock_is_transaction_scoped(self):
        session = Mock()
        session.bind.dialect.name = 'postgresql'
        write_lock(session)
        self.assertIn('pg_advisory_xact_lock', str(session.execute.call_args.args[0]))
        session.connection.assert_not_called()

    def test_snapshot_is_read_only_and_nonpostgres_target_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.sqlite3'
            engine = engine_for(path)
            try:
                initialize(engine)
                before = hashlib.sha256(path.read_bytes()).hexdigest()
                snapshot = read_snapshot(path)
                self.assertEqual(snapshot['clockwork_application_schema'], [{'id': 1, 'version': 3}])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
                with self.assertRaises(ValueError):
                    copy_snapshot(snapshot, engine)
            finally:
                engine.dispose()
            missing = Path(directory) / 'missing.sqlite3'
            with self.assertRaises(Exception):
                read_snapshot(missing)
            self.assertFalse(missing.exists())
