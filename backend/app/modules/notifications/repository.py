from datetime import datetime, timezone
from .schemas import NotificationJob


def enqueue(db, job: NotificationJob, session):
    """Durable outbox in notification_jobs, inside the domain transaction.

    No external delivery or worker is implemented in Phase 1.
    """
    record = job.model_dump()
    record.update(schema_version=1, status='pending', attempts=0, max_attempts=3,
                  created_at=datetime.now(timezone.utc), next_attempt_at=datetime.now(timezone.utc))
    db.notification_jobs.update_one({'idempotency_key': job.idempotency_key},
                                    {'$setOnInsert': record}, upsert=True, session=session)
