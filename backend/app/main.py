"""
VoxParaguay 2026 - Main FastAPI Application
Multi-channel polling and sentiment analysis platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import webhooks, campaigns, agents, responses, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Locale: {settings.DEFAULT_LOCALE} | Timezone: {settings.TIMEZONE}")
    yield
    # Shutdown
    print("👋 Shutting down VoxParaguay 2026")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de encuestas multicanal y análisis de opinión pública para Paraguay",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campañas"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agentes"])
app.include_router(responses.router, prefix="/api/responses", tags=["Respuestas"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Análisis"])


@app.get("/")
async def root():
    return {
        "nombre": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "activo",
        "locale": settings.DEFAULT_LOCALE,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voxparaguay-backend"}
