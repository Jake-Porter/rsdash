import logging

import httpx

WIKI_API = "https://runescape.wiki/api.php"
HEADERS = {"User-Agent": "rsdash-personal-tracker/1.0 (github.com/Jake-Porter/rsdash)"}

log = logging.getLogger("rsdash.wiki_icons")

# cache_key ("skill:Attack", "activity:Dominion Tower", "task:Daily Challenges") -> resolved image URL.
# Only positive hits are stored; misses are simply retried on the next poll (cheap, infrequent).
_cache: dict[str, str] = {}


def get_cached(kind: str, name: str) -> str | None:
    return _cache.get(f"{kind}:{name}")


async def _query_titles_batch(titles: list[str]) -> dict[str, str]:
    """Resolve a batch of File: titles to image URLs. Returns only titles that exist."""
    found: dict[str, str] = {}
    if not titles:
        return found
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        for i in range(0, len(titles), 50):
            chunk = titles[i : i + 50]
            joined = "|".join(f"File:{t}" for t in chunk)
            try:
                resp = await client.get(
                    WIKI_API,
                    params={
                        "action": "query",
                        "titles": joined,
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "format": "json",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                log.warning("wiki icon batch lookup failed", exc_info=True)
                continue
            for page in data.get("query", {}).get("pages", {}).values():
                if "missing" in page:
                    continue
                info = page.get("imageinfo")
                title = page.get("title", "")
                if info and title.startswith("File:"):
                    found[title.removeprefix("File:")] = info[0]["url"]
    return found


async def resolve(kind: str, items: dict[str, list[str]]) -> None:
    """
    items: {name: [candidate wiki filenames in priority order]}.
    Populates the module cache in place for whichever names resolve; already-cached
    names are skipped. Safe to call repeatedly (e.g. every poll) — cheap no-op once warm.
    """
    pending = {name: cands for name, cands in items.items() if f"{kind}:{name}" not in _cache}
    if not pending:
        return
    all_candidates = [c for cands in pending.values() for c in cands]
    found = await _query_titles_batch(all_candidates)
    for name, candidates in pending.items():
        for candidate in candidates:
            if candidate in found:
                _cache[f"{kind}:{name}"] = found[candidate]
                break
