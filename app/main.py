from fastapi import FastAPI

app = FastAPI(title = "Pingboard")

TARGETS = [
{"name": "Riot Games", "url": "https://riotgames.com"}, 
{"name": "Steam", "url": "https://steam.com"}, 
{"name": "Google", "url": "https://google.com"}
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