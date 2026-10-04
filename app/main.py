import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import time

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import get_uptime, init_db, save_results, get_last_down

from app.checker import check_all
from app.config import load_targets

from pathlib import Path

SLOW_THRESHOLD_MS = 500
CHECK_INTERVAL_SECONDS = 30
latest = {"checked_at": None, "results": []}

templates = Jinja2Templates(directory  = Path(__file__).parent / "templates")

async def check_loop():
    while True:
        try:
            start = time.perf_counter()
            results = await check_all(load_targets())
            checked_at = datetime.now(timezone.utc).isoformat()
            save_results(checked_at, results)
            latest["results"] = results
            latest["checked_at"] = checked_at
            latest["duration_ms"] = round((time.perf_counter() - start) * 1000)
        except Exception as error:
            print(f"Check round failed: {error!r}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(check_loop())
    yield
    task.cancel()


app = FastAPI(title="Pingboard", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    uptime_by_name = {row["name"]: row for row in get_uptime(24)}
    return templates.TemplateResponse(
        request, "index.html", {"latest": latest, "uptime": uptime_by_name, "SLOW_THRESHOLD_MS": SLOW_THRESHOLD_MS}
    )

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/api/targets")
def targets():
    return load_targets()

@app.get("/api/status")
def status():
    return latest

@app.get("/api/uptime")
def uptime(hours : int = 24):
    return get_uptime(hours)

@app.get("/api/lastdown")
def lastdown(hours : int = 24):
    return get_last_down(hours)
