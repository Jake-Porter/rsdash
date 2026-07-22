from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app import config
from app.db import get_conn, get_or_create_account
from app.icons import task_icon
from app.templating import templates
from app.weekbounds import current_day_start, current_week_start, period_start

router = APIRouter()

DEFAULT_TASKS = [
    ("daily", "Daily Challenges"),
    ("daily", "POF"),
    ("daily", "Player Owned Ports"),
    ("weekly", "Old Man Potato Cactus"),
    ("weekly", "Shop Run: Meat"),
    ("weekly", "Shop Run: Runes"),
    ("weekly", "Tears of Guthix"),
    ("weekly", "Herby Werby"),
    ("weekly", "Pineapple Runs (Catherby and Karajama)"),
    ("weekly", "Managing Misc"),
]


def _seed_default_tasks(conn, account_id: int) -> None:
    existing = conn.execute(
        "SELECT COUNT(*) c FROM weekly_tasks WHERE account_id=?", (account_id,)
    ).fetchone()["c"]
    if existing:
        return
    for i, (category, name) in enumerate(DEFAULT_TASKS):
        conn.execute(
            "INSERT INTO weekly_tasks(account_id, name, category, sort_order) VALUES (?,?,?,?)",
            (account_id, name, category, i),
        )
    conn.commit()


@router.get("/weekly")
def weekly_page(request: Request):
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    day_start = current_day_start()
    week_start = current_week_start()
    conn = get_conn()
    try:
        _seed_default_tasks(conn, account_id)

        tasks = conn.execute(
            "SELECT * FROM weekly_tasks WHERE account_id=? AND active=1 ORDER BY category DESC, sort_order, id",
            (account_id,),
        ).fetchall()

        completions = {}
        for cat, boundary in (("daily", day_start), ("weekly", week_start)):
            for r in conn.execute(
                """SELECT wc.task_id, wc.completed_at FROM weekly_completions wc
                   JOIN weekly_tasks wt ON wt.id = wc.task_id
                   WHERE wt.category=? AND wc.period_start=?""",
                (cat, boundary.isoformat()),
            ).fetchall():
                completions[r["task_id"]] = r["completed_at"]

        last_completed = {}
        for t in tasks:
            row = conn.execute(
                "SELECT completed_at FROM weekly_completions WHERE task_id=? ORDER BY completed_at DESC LIMIT 1",
                (t["id"],),
            ).fetchone()
            last_completed[t["id"]] = row["completed_at"] if row else None
    finally:
        conn.close()

    dailies = [t for t in tasks if t["category"] == "daily"]
    weeklies = [t for t in tasks if t["category"] == "weekly"]

    return templates.TemplateResponse(
        request,
        "weekly.html",
        {
            "dailies": dailies,
            "weeklies": weeklies,
            "completions": completions,
            "last_completed": last_completed,
            "day_start": day_start,
            "week_start": week_start,
            "task_icon": task_icon,
        },
    )


@router.post("/weekly/add")
def add_task(name: str = Form(...), description: str = Form(""), category: str = Form("weekly")):
    if category not in ("daily", "weekly"):
        category = "weekly"
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    conn = get_conn()
    try:
        max_sort = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM weekly_tasks WHERE account_id=? AND category=?",
            (account_id, category),
        ).fetchone()["n"]
        conn.execute(
            "INSERT INTO weekly_tasks(account_id, name, description, category, sort_order) VALUES (?,?,?,?,?)",
            (account_id, name.strip(), description.strip(), category, max_sort),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/weekly", status_code=303)


@router.post("/weekly/{task_id}/toggle")
def toggle_task(task_id: int):
    conn = get_conn()
    try:
        task = conn.execute("SELECT category FROM weekly_tasks WHERE id=?", (task_id,)).fetchone()
        if not task:
            return RedirectResponse("/weekly", status_code=303)
        boundary = period_start(task["category"]).isoformat()
        existing = conn.execute(
            "SELECT id FROM weekly_completions WHERE task_id=? AND period_start=?",
            (task_id, boundary),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM weekly_completions WHERE id=?", (existing["id"],))
        else:
            conn.execute(
                "INSERT INTO weekly_completions(task_id, period_start, completed_at) VALUES (?,?,?)",
                (task_id, boundary, datetime.now(timezone.utc).isoformat()),
            )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/weekly", status_code=303)


@router.post("/weekly/{task_id}/delete")
def delete_task(task_id: int):
    conn = get_conn()
    try:
        conn.execute("UPDATE weekly_tasks SET active=0 WHERE id=?", (task_id,))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/weekly", status_code=303)
