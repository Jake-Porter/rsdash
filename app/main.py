import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import wiki_icons
from app.db import init_db
from app.icons import task_icon_candidates
from app.routers import feed, goals, stats, weekly
from app.routers.weekly import DEFAULT_TASKS
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        await wiki_icons.resolve(
            "task", {name: task_icon_candidates(name) for _, name in DEFAULT_TASKS}
        )
    except Exception:
        logging.getLogger("rsdash.main").warning("task icon resolution failed", exc_info=True)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="rsdash", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(stats.router)
app.include_router(weekly.router)
app.include_router(goals.router)
app.include_router(feed.router)
