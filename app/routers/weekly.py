from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app import config
from app.db import get_conn, get_or_create_account
from app.templating import templates
from app.weekbounds import current_week_start

router = APIRouter()


@router.get("/weekly")
def weekly_page(request: Request):
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    week_start = current_week_start()
    conn = get_conn()
    try:
        tasks = conn.execute(
            "SELECT * FROM weekly_tasks WHERE account_id=? AND active=1 ORDER BY sort_order, id",
            (account_id,),
        ).fetchall()
        completions = {
            r["task_id"]: r["completed_at"]
            for r in conn.execute(
                "SELECT task_id, completed_at FROM weekly_completions WHERE week_start=?",
                (week_start.isoformat(),),
            ).fetchall()
        }
        last_completed = {}
        for t in tasks:
            row = conn.execute(
                "SELECT completed_at FROM weekly_completions WHERE task_id=? ORDER BY completed_at DESC LIMIT 1",
                (t["id"],),
            ).fetchone()
            last_completed[t["id"]] = row["completed_at"] if row else None
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "weekly.html",
        {
            "tasks": tasks,
            "completions": completions,
            "last_completed": last_completed,
            "week_start": week_start,
        },
    )


@router.post("/weekly/add")
def add_task(name: str = Form(...), description: str = Form("")):
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    conn = get_conn()
    try:
        max_sort = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS n FROM weekly_tasks WHERE account_id=?",
            (account_id,),
        ).fetchone()["n"]
        conn.execute(
            "INSERT INTO weekly_tasks(account_id, name, description, sort_order) VALUES (?,?,?,?)",
            (account_id, name.strip(), description.strip(), max_sort),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/weekly", status_code=303)


@router.post("/weekly/{task_id}/toggle")
def toggle_task(task_id: int):
    week_start = current_week_start().isoformat()
    conn = get_conn()
    try:
        existing = conn.execute(
            "SELECT id FROM weekly_completions WHERE task_id=? AND week_start=?",
            (task_id, week_start),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM weekly_completions WHERE id=?", (existing["id"],))
        else:
            conn.execute(
                "INSERT INTO weekly_completions(task_id, week_start, completed_at) VALUES (?,?,?)",
                (task_id, week_start, datetime.now(timezone.utc).isoformat()),
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
