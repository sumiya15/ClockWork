import unittest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.app.main import create_app
from backend.app.core.settings import Settings


class OfflineTests(unittest.TestCase):
    def test_database_failure_keeps_liveness_but_fails_readiness(self):
        settings = Settings(mongo_uri='mongodb://127.0.0.1:1/',mongo_database='clockwork_test_unreachable')
        with TestClient(create_app(settings)) as http:
            self.assertEqual(http.get('/api/v1/health/live').status_code,200)
            self.assertEqual(http.get('/api/v1/health/ready').status_code,503)
            self.assertEqual(http.get('/api/v1/obligations').status_code,503)

    def test_settings_reject_dangerous_mode_and_origins(self):
        for values in ({'mongo_database':'clockwork_live_x'}, {'allowed_origins':['*']},
                       {'mode':'real'}, {'allowed_origins':['http://public.example']}):
            with self.assertRaises(ValidationError):
                Settings(**values)
