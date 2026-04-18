from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
from services.vector_store import list_documents


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     docs = list_documents()
#     if len(docs) == 0:
#         print("🧠 Knowledge base empty — running batch ingestion...")
#         from ingestion.batch_ingest import run
#         run()
#         print("🧠 Ingestion complete")
#     else:
#         print(f"🧠 Knowledge base loaded: {len(docs)} docs")
#     yield


app = FastAPI(
    title="0xbrain",
    description="RAG system for crypto knowledge",
    version="0.1.0",
    # lifespan=lifespan,
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