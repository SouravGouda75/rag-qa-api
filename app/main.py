import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.ingest import router as ingest_router
from app.api.query import router as query_router
from app.core.retriever import get_collection_stats
from app.models.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger(__name__)
    logger.info("Pre-warming embedding model to prevent query cold-start...")
    try:
        from app.core.embedder import get_embedder
        from app.config import settings
        get_embedder(settings.embedding_model)
        logger.info("Embedding model pre-warmed.")
    except Exception as e:
        logger.warning(f"Startup warm-up skipped: {e}")
    yield


app = FastAPI(
    title="RAG API",
    description="A retrieval-augmented generation API for document question answering",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(query_router, tags=["Query"])


@app.get("/health", response_model=HealthResponse)
async def health_check():
    stats = get_collection_stats()
    return HealthResponse(
        status="healthy",
        documents_count=stats["documents_count"],
        chunks_count=stats["chunks_count"],
    )
