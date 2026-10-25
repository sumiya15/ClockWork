from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def baseline_due(started_at, duration_days, timezone_name):
    """N calendar dates after the configured start event, through local day end.

    MongoDB timestamps have millisecond precision, so use .999, not .999999.
    """
    zone = ZoneInfo(timezone_name)
    date = started_at.astimezone(zone).date() + timedelta(days=duration_days)
    return datetime.combine(date, time(23, 59, 59, 999000), zone).astimezone(timezone.utc)
