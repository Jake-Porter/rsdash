from fastapi import APIRouter, Request

from app import config
from app.db import get_account_id, get_conn
from app.icons import feed_icon
from app.templating import templates

router = APIRouter()


@router.get("/feed")
def feed_page(request: Request, filter: str = "all"):
    account_id = get_account_id("rs3", config.RSN_RS3)
    conn = get_conn()
    try:
        if account_id:
            if filter and filter != "all":
                rows = conn.execute(
                    "SELECT * FROM activity_feed WHERE account_id=? AND event_type=? ORDER BY id DESC LIMIT 200",
                    (account_id, filter),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM activity_feed WHERE account_id=? ORDER BY id DESC LIMIT 200",
                    (account_id,),
                ).fetchall()
        else:
            rows = []
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "feed.html",
        {"rows": rows, "filter": filter, "rsn": config.RSN_RS3, "feed_icon": feed_icon},
    )
