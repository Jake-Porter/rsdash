from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

LOCAL_TZ = ZoneInfo("America/Denver")


def local_dt(value):
    """Format a stored UTC ISO timestamp as a friendly local (Mountain Time) string."""
    if not value:
        return value
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return value
    return dt.astimezone(LOCAL_TZ).strftime("%b %d, %Y %I:%M %p")


templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.filters["local_dt"] = local_dt
