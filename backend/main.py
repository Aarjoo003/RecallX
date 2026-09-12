"""
RecallX Backend - Semantic Conversation Intelligence Engine
FastAPI Application Entrypoint
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend package is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app.api.routes import router as api_router
from app.indexing.index_manager import IndexManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for pre-loading dense embeddings and SQLite indexes
    into memory on startup so search queries execute in under 20ms.
    """
    print("[RecallX] Initializing Semantic Index & Embedding Engine...")
    mgr = IndexManager.get_instance()
    mgr.initialize()
    print(f"[RecallX] Retrieval Engine ready! ({len(mgr.idx_to_id)} indexed messages)")
    yield
    print("[RecallX] Shutting down...")


app = FastAPI(
    title="RecallX - Semantic Conversation Intelligence API",
    description="Search what your group meant — not just what they typed. Hybrid lexical-semantic retrieval for group chat archives.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware supporting local development and production Vercel frontend
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    for local_origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]:
        if local_origin not in origins:
            origins.append(local_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False if "*" in origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core API routes
app.include_router(api_router)


@app.get("/health")
def health():
    mgr = IndexManager.get_instance()
    return {
        "status": "healthy",
        "service": "RecallX Semantic Retrieval Engine",
        "index_ready": mgr.is_ready,
        "indexed_messages": len(mgr.idx_to_id) if mgr.is_ready else 0,
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {
        "name": "RecallX Semantic Retrieval Engine",
        "version": "1.0.0",
        "tagline": "Search what your group meant — not just what they typed.",
        "docs_url": "/docs",
        "health_check": "/health",
        "api_endpoints": {
            "health": "/api/health",
            "search": "/api/search",
            "decisions": "/api/decisions",
            "participants": "/api/participants",
            "evaluation": "/api/evaluation",
            "thread": "/api/thread/{thread_id}",
            "context": "/api/context/{message_id}",
        },
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
