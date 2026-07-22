from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app import config
from app.db import get_conn, get_or_create_account
from app.templating import templates

router = APIRouter()


@router.get("/goals")
def goals_page(request: Request):
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    conn = get_conn()
    try:
        goals = conn.execute(
            "SELECT * FROM goals WHERE account_id=? ORDER BY status, created_at DESC",
            (account_id,),
        ).fetchall()
        updates_by_goal = {}
        for g in goals:
            updates_by_goal[g["id"]] = conn.execute(
                "SELECT * FROM goal_updates WHERE goal_id=? ORDER BY created_at DESC",
                (g["id"],),
            ).fetchall()
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "goals.html",
        {"goals": goals, "updates_by_goal": updates_by_goal},
    )


@router.post("/goals/add")
def add_goal(title: str = Form(...), notes: str = Form("")):
    account_id = get_or_create_account("rs3", config.RSN_RS3)
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO goals(account_id, title, notes, status, created_at) VALUES (?,?,?,'open',?)",
            (account_id, title.strip(), notes.strip(), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/goals", status_code=303)


@router.post("/goals/{goal_id}/toggle")
def toggle_goal(goal_id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT status FROM goals WHERE id=?", (goal_id,)).fetchone()
        if row:
            new_status = "open" if row["status"] == "done" else "done"
            completed_at = datetime.now(timezone.utc).isoformat() if new_status == "done" else None
            conn.execute(
                "UPDATE goals SET status=?, completed_at=? WHERE id=?",
                (new_status, completed_at, goal_id),
            )
            conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/goals", status_code=303)


@router.post("/goals/{goal_id}/updates")
def add_goal_update(goal_id: int, note: str = Form(...)):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO goal_updates(goal_id, note, created_at) VALUES (?,?,?)",
            (goal_id, note.strip(), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/goals", status_code=303)


@router.post("/goals/{goal_id}/delete")
def delete_goal(goal_id: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM goal_updates WHERE goal_id=?", (goal_id,))
        conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
        conn.commit()
    finally:
        conn.close()
    return RedirectResponse("/goals", status_code=303)
