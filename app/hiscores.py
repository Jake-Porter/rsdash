import httpx

HISCORES_URLS = {
    "rs3": "https://secure.runescape.com/m=hiscore/index_lite.json",
    "osrs": "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json",
}

HEADERS = {"User-Agent": "rsdash-personal-tracker/1.0"}


async def fetch_hiscores(game: str, rsn: str) -> dict:
    url = HISCORES_URLS[game]
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        resp = await client.get(url, params={"player": rsn})
        resp.raise_for_status()
        return resp.json()
