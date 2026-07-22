import hashlib

import httpx

PROFILE_URL = "https://apps.runescape.com/runemetrics/profile/profile"
HEADERS = {"User-Agent": "rsdash-personal-tracker/1.0"}


class RuneMetricsError(Exception):
    pass


async def fetch_adventurers_log(rsn: str, count: int = 20) -> list[dict]:
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        resp = await client.get(PROFILE_URL, params={"user": rsn, "activities": count})
        resp.raise_for_status()
        data = resp.json()
    if isinstance(data, dict) and data.get("error"):
        raise RuneMetricsError(data["error"])
    return data.get("activities", [])


def classify_activity(text: str, details: str) -> str:
    lowered = text.lower()
    if lowered.startswith("i found") or lowered.startswith("i looted") or "i received" in lowered:
        return "drop"
    if lowered.startswith("i killed") or "i defeated" in lowered:
        return "boss_kill"
    if "quest complete" in lowered or lowered.startswith("i have completed"):
        return "quest"
    if "xp in" in lowered or "experience points" in details.lower():
        return "xp_milestone"
    return "other"


def entry_hash(rsn: str, date: str, text: str) -> str:
    return hashlib.sha256(f"{rsn}|{date}|{text}".encode()).hexdigest()
