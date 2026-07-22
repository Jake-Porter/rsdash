import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_PATH = os.environ.get("DB_PATH", "/app/data/rsdash.db")
RSN_RS3 = os.environ.get("RSN_RS3", "").strip()
RSN_OSRS = os.environ.get("RSN_OSRS", "").strip()
HISCORES_POLL_MINUTES = int(os.environ.get("HISCORES_POLL_MINUTES", "30"))
FEED_POLL_MINUTES = int(os.environ.get("FEED_POLL_MINUTES", "15"))
