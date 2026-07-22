import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import config
from app.db import get_conn, get_or_create_account
from app.hiscores import fetch_hiscores
from app.runemetrics import (
    RuneMetricsError,
    classify_activity,
    entry_hash,
    fetch_adventurers_log,
)

log = logging.getLogger("rsdash.scheduler")
scheduler = AsyncIOScheduler()


async def poll_hiscores_for(game: str, rsn: str) -> None:
    if not rsn:
        return
    account_id = get_or_create_account(game, rsn)
    try:
        data = await fetch_hiscores(game, rsn)
    except Exception:
        log.exception("hiscores poll failed for %s/%s", game, rsn)
        return

    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        for skill in data.get("skills", []):
            if skill.get("xp", -1) < 0:
                continue
            conn.execute(
                "INSERT INTO xp_snapshots(account_id, skill, level, xp, captured_at) VALUES (?,?,?,?,?)",
                (account_id, skill["name"], skill["level"], skill["xp"], now),
            )
        for activity in data.get("activities", []):
            if activity.get("score", -1) < 0:
                continue
            conn.execute(
                "INSERT INTO boss_kc_snapshots(account_id, activity, score, captured_at) VALUES (?,?,?,?)",
                (account_id, activity["name"], activity["score"], now),
            )
        conn.commit()
    finally:
        conn.close()
    log.info("hiscores poll ok for %s/%s", game, rsn)


async def poll_feed_for(rsn: str) -> None:
    if not rsn:
        return
    account_id = get_or_create_account("rs3", rsn)
    try:
        activities = await fetch_adventurers_log(rsn)
    except RuneMetricsError as exc:
        log.warning("adventurer's log unavailable for %s: %s", rsn, exc)
        return
    except Exception:
        log.exception("adventurer's log poll failed for %s", rsn)
        return

    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        for entry in activities:
            text = entry.get("text", "")
            details = entry.get("details", "")
            date = entry.get("date", "")
            h = entry_hash(rsn, date, text)
            event_type = classify_activity(text, details)
            conn.execute(
                """INSERT OR IGNORE INTO activity_feed
                   (account_id, event_type, text, details, occurred_at, raw_hash, fetched_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (account_id, event_type, text, details, date, h, now),
            )
        conn.commit()
    finally:
        conn.close()
    log.info("adventurer's log poll ok for %s (%d entries)", rsn, len(activities))


async def poll_all_hiscores() -> None:
    await poll_hiscores_for("rs3", config.RSN_RS3)
    await poll_hiscores_for("osrs", config.RSN_OSRS)


async def poll_all_feeds() -> None:
    await poll_feed_for(config.RSN_RS3)


def start_scheduler() -> None:
    scheduler.add_job(
        poll_all_hiscores, "interval",
        minutes=config.HISCORES_POLL_MINUTES,
        next_run_time=datetime.now(),
        id="poll_hiscores",
    )
    scheduler.add_job(
        poll_all_feeds, "interval",
        minutes=config.FEED_POLL_MINUTES,
        next_run_time=datetime.now(),
        id="poll_feeds",
    )
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
