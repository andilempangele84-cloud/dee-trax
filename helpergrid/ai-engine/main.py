#!/usr/bin/env python3
"""
HelperGrid AI Engine - Main Application Entry Point

Core FastAPI application that manages:
- LLM provider integration
- NLP processing pipeline
- Agent orchestration
- Vector database operations
- Real-time WebSocket connections
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse

from config.environment import settings
from config.logging_config import setup_logging
from middleware.error_handler import GlobalExceptionHandler
from middleware.auth_middleware import AuthMiddleware
from routes import (
    llm_routes,
    agent_routes,
    nlp_routes,
    embedding_routes,
    health_routes,
    integration_routes,
)

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    
    # Initialize services
    from services.llm_service import LLMService
    from services.vector_db_service import VectorDBService
    from services.cache_service import CacheService
    
    try:
        llm_service = LLMService()
        await llm_service.initialize()
        logger.info("✅ LLM Service initialized")
        
        vector_db = VectorDBService()
        await vector_db.initialize()
        logger.info("✅ Vector DB Service initialized")
        
        cache_service = CacheService()
        await cache_service.initialize()
        logger.info("✅ Cache Service initialized")
        
        app.state.llm_service = llm_service
        app.state.vector_db = vector_db
        app.state.cache_service = cache_service
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down services...")
    try:
        await llm_service.shutdown()
        await vector_db.shutdown()
        await cache_service.shutdown()
        logger.info("✅ All services shutdown successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Engine for HelperGrid Marketplace - LLM Integration, NLP Processing & Agent Orchestration",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# Add global exception handler
app.add_exception_handler(Exception, GlobalExceptionHandler)


# Include routers
app.include_router(health_routes.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(llm_routes.router, prefix="/api/v1/llm", tags=["LLM"])
app.include_router(agent_routes.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(nlp_routes.router, prefix="/api/v1/nlp", tags=["NLP"])
app.include_router(embedding_routes.router, prefix="/api/v1/embeddings", tags=["Embeddings"])
app.include_router(integration_routes.router, prefix="/api/v1/integrations", tags=["Integrations"])


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint - API status and information
    """
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "Not available",
    }


@app.get("/health/ready", tags=["Health"])
async def readiness() -> JSONResponse:
    """
    Readiness probe - checks if service is ready to accept traffic
    """
    try:
        # Check critical services
        cache = app.state.cache_service
        llm = app.state.llm_service
        
        cache_ok = await cache.health_check()
        llm_ok = await llm.health_check()
        
        if cache_ok and llm_ok:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "ready", "timestamp": os.getenv("TIMESTAMP", "")}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "reason": "Service check failed"}
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "message": str(e)}
        )


if __name__ == "__main__":
    """
    Run the application using Uvicorn
    """
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if settings.ENVIRONMENT == "production" else 1,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
