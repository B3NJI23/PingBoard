from fastapi import FastAPI

from app.checker import check_http

app = FastAPI(title = "Pingboard")

TARGETS = [
{"name": "Riot Games", "url": "https://riotgames.com"}, 
{"name": "Steam", "url": "https://store.steampowered.com"}, 
{"name": "Google", "url": "https://google.com"},
{"name": "TEST", "url": "https://this-site-does-not-exist-pingboard.com"}
]

@app.get("/")
def home():
    return {"message": "Pingboard is alive!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/api/targets")
def targets():
    return TARGETS

@app.get("/api/status")
def status():
    results = []
    for target in TARGETS:
        result = check_http(target["url"])
        result["name"] = target["name"]
        results.append(result)

    return results