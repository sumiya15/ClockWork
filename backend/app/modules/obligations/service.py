from datetime import timedelta
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from ..auth.guards import obligation_scope
from ...core.errors import object_id
from . import repository
from .schemas import Obligation, ObligationView, ObligationPage


def view(row, now, timezone_name):
    item = Obligation(id=row['_id'], **{k: v for k, v in row.items() if k != '_id'})
    due = item.active_due_at
    if item.paused_at:
        due += max(now - item.paused_at, timedelta())
    zone = ZoneInfo(timezone_name)
    remaining = (due.astimezone(zone).date() - now.astimezone(zone).date()).days
    severity = ('overdue' if remaining < 0 else 'due_today' if remaining == 0 else
                'due_soon' if remaining <= 7 else 'active')
    if item.state in ('completed', 'cancelled'):
        severity = item.state
    return ObligationView(**{**item.model_dump(), 'active_due_at': due}, days_remaining=remaining, deadline_severity=severity)


def page(db, user, clock, settings, filters, limit, offset):
    rows, total = repository.page(db, obligation_scope(user), filters, limit, offset)
    now = clock.now()
    return ObligationPage(items=[view(row, now, settings.business_timezone) for row in rows],
                          total=total, limit=limit, offset=offset, business_at=now)


def get(db, user, clock, settings, identifier):
    row = repository.get(db, obligation_scope(user), object_id(identifier))
    if not row:
        raise HTTPException(404, 'Obligation not found')
    return view(row, clock.now(), settings.business_timezone)
