from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.api.v1 import chat, logs, generate, analyze, health

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI DevOps Copilot API", version=settings.VERSION)
    yield
    logger.info("Shutting down AI DevOps Copilot API")


app = FastAPI(
    title="AI DevOps Copilot API",
    description="AI-powered DevOps assistant with Bedrock integration",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["generate"])
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["analyze"])

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


@app.get("/")
async def root():
    return {
        "service": "AI DevOps Copilot API",
        "version": settings.VERSION,
        "status": "running",
    }
