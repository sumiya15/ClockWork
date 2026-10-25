"""Business time is injected; security always uses real UTC directly."""
from datetime import datetime, timezone


class RealClock:
    def now(self):
        return datetime.now(timezone.utc)


class DemoClock:
    def __init__(self, db):
        if not db.name.startswith(('clockwork_demo_', 'clockwork_test_')):
            raise ValueError('Demo clock requires an isolated database')
        self.db = db

    def now(self):
        state = self.db.checkpoints.find_one({'_id': 'demo_clock'})
        if not state:
            raise RuntimeError('Demo clock is not seeded')
        return state['business_at']
