from fastapi import FastAPI

app = FastAPI(title = "Pingboard")

@app.get("/")
def home():
    return {"message": "Pingboard is alive!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}