import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import time

from fastapi import FastAPI

from app.checker import check_all
from app.config import load_targets

CHECK_INTERVAL_SECONDS = 60
latest = {"checked_at": None, "results": []}


async def check_loop():
    while True:
        try:
            start = time.perf_counter()
            latest["results"] = await check_all(load_targets())
            latest["duration_ms"] = round((time.perf_counter() - start) * 1000)
            latest["checked_at"] = datetime.now(timezone.utc).isoformat()
        except Exception as error:
            print(f"Check round failed: {error!r}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
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