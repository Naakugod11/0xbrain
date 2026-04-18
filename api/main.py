from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router

app = FastAPI(
    title="0xbrain",
    description="RAG system for crypto knowledge - query whitepapers and protocol docs with sourced AI answers",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/demo", StaticFiles(directory="frontend", html=True), name="demo")

@app.get("/health")
async def health():
    return {"status": "alive"}