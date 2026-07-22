from fastapi import APIRouter, Request

from app import config
from app.db import get_account_id, get_conn
from app.icons import activity_icon, feed_icon, skill_icon, task_icon
from app.templating import templates
from app.weekbounds import current_day_start, current_week_start

router = APIRouter()


def _latest_xp_rows(conn, account_id: int):
    return conn.execute(
        """
        SELECT skill, level, xp, captured_at FROM xp_snapshots
        WHERE account_id = ? AND captured_at = (
            SELECT MAX(captured_at) FROM xp_snapshots WHERE account_id = ?
        )
        ORDER BY skill != 'Overall', skill
        """,
        (account_id, account_id),
    ).fetchall()


def _latest_kc_rows(conn, account_id: int):
    return conn.execute(
        """
        SELECT activity, score, captured_at FROM boss_kc_snapshots
        WHERE account_id = ? AND captured_at = (
            SELECT MAX(captured_at) FROM boss_kc_snapshots WHERE account_id = ?
        )
        ORDER BY score DESC
        """,
        (account_id, account_id),
    ).fetchall()


@router.get("/")
def home(request: Request):
    conn = get_conn()
    try:
        account_id = get_account_id("rs3", config.RSN_RS3)
        overall = None
        open_goals = 0
        task_summary = []
        recent_feed = []
        last_synced = None
        if account_id:
            xp_rows = _latest_xp_rows(conn, account_id)
            overall = next((r for r in xp_rows if r["skill"] == "Overall"), None)
            last_synced = xp_rows[0]["captured_at"] if xp_rows else None
            open_goals = conn.execute(
                "SELECT COUNT(*) c FROM goals WHERE account_id=? AND status='open'",
                (account_id,),
            ).fetchone()["c"]

            tasks = conn.execute(
                "SELECT id, name, category FROM weekly_tasks WHERE account_id=? AND active=1 ORDER BY category DESC, sort_order, id",
                (account_id,),
            ).fetchall()
            day_start = current_day_start().isoformat()
            week_start = current_week_start().isoformat()
            done_ids = set()
            for cat, boundary in (("daily", day_start), ("weekly", week_start)):
                for r in conn.execute(
                    """SELECT wc.task_id FROM weekly_completions wc
                       JOIN weekly_tasks wt ON wt.id = wc.task_id
                       WHERE wt.category=? AND wc.period_start=?""",
                    (cat, boundary),
                ).fetchall():
                    done_ids.add(r["task_id"])
            task_summary = [
                {"name": t["name"], "category": t["category"], "icon": task_icon(t["name"], t["category"]), "done": t["id"] in done_ids}
                for t in tasks
            ]
            recent_feed = conn.execute(
                "SELECT event_type, text, occurred_at FROM activity_feed WHERE account_id=? ORDER BY id DESC LIMIT 8",
                (account_id,),
            ).fetchall()
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "rsn": config.RSN_RS3,
            "overall": overall,
            "last_synced": last_synced,
            "open_goals": open_goals,
            "task_summary": task_summary,
            "recent_feed": recent_feed,
            "feed_icon": feed_icon,
        },
    )


@router.get("/xp")
def xp_page(request: Request):
    conn = get_conn()
    try:
        account_id = get_account_id("rs3", config.RSN_RS3)
        rows = _latest_xp_rows(conn, account_id) if account_id else []
    finally:
        conn.close()
    return templates.TemplateResponse(
        request, "xp.html", {"rsn": config.RSN_RS3, "rows": rows, "skill_icon": skill_icon}
    )


@router.get("/kc")
def kc_page(request: Request):
    conn = get_conn()
    try:
        account_id = get_account_id("rs3", config.RSN_RS3)
        rows = _latest_kc_rows(conn, account_id) if account_id else []
    finally:
        conn.close()
    return templates.TemplateResponse(
        request, "kc.html", {"rsn": config.RSN_RS3, "rows": rows, "activity_icon": activity_icon}
    )
