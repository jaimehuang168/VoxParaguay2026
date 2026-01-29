"""
VoxParaguay 2026 - Main FastAPI Application
Multi-channel polling and sentiment analysis platform
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

from app.core.config import settings
from app.api.routes import webhooks, campaigns, agents, responses, analytics, respondents, analysis, summary
from app.services.sentiment_service import get_sentiment_service


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

# Include routers (v1 API)
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campañas"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agentes"])
app.include_router(responses.router, prefix="/api/v1/responses", tags=["Respuestas"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Análisis"])
app.include_router(respondents.router, prefix="/api/v1/respondents", tags=["Encuestados"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Análisis IA"])
app.include_router(summary.router, prefix="/api/v1/summary", tags=["Resumen IA"])


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


# ============ WEBSOCKET ENDPOINT ============

@app.websocket("/ws/sentiment")
async def websocket_sentiment(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sentiment updates.

    Connect to receive live sentiment data as surveys are processed.
    The client will receive JSON messages with the following structure:
    {
        "type": "sentiment_update",
        "department_id": "PY-ASU",
        "sentiment_score": 0.15,
        "average": 0.08,
        "total_count": 42,
        "timestamp": "2026-01-29T12:34:56",
        "metadata": {...}
    }

    On connection, the client receives current sentiment data for all departments.
    """
    await websocket.accept()

    service = get_sentiment_service()

    # Register this WebSocket for broadcasts
    await service.register_websocket(websocket)

    try:
        # Send initial state (all current sentiments)
        current_sentiments = await service.get_all_sentiments()
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "sentiments": current_sentiments,
            "message": "Connected to VoxParaguay sentiment stream",
        }))

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message (ping/pong or commands)
                data = await websocket.receive_text()

                # Handle ping
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                # Handle request for current state
                elif data == "get_state":
                    current_sentiments = await service.get_all_sentiments()
                    await websocket.send_text(json.dumps({
                        "type": "state",
                        "sentiments": current_sentiments,
                    }))

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        # Unregister on disconnect
        await service.unregister_websocket(websocket)
