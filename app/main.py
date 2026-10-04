import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import time

from fastapi import FastAPI

from app.db import get_uptime, init_db, save_results, get_last_down

from app.checker import check_all
from app.config import load_targets

CHECK_INTERVAL_SECONDS = 60
latest = {"checked_at": None, "results": []}


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

@app.get("/")
def home():
    return {"message": "Pingboard is alive!"}

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
