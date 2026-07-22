from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Denver")
RESET_WEEKDAY = 1  # Monday=0 .. Tuesday=1
RESET_HOUR = 18  # 6 PM local (MST or MDT, DST-aware via zoneinfo)


def current_week_start(now: datetime | None = None) -> datetime:
    """Most recent Tuesday 18:00 America/Denver at or before `now`."""
    now = (now or datetime.now(TZ)).astimezone(TZ)
    candidate = now.replace(hour=RESET_HOUR, minute=0, second=0, microsecond=0)
    days_since_reset = (candidate.weekday() - RESET_WEEKDAY) % 7
    candidate -= timedelta(days=days_since_reset)
    if candidate > now:
        candidate -= timedelta(days=7)
    return candidate
