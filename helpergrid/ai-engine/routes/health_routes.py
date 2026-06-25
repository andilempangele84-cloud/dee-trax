#!/usr/bin/env python3
"""
Health Check Routes

Endpoints for service health monitoring and readiness checks
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger

router = APIRouter()


@router.get("/live")
async def liveness():
    """
    Liveness probe - indicates if service is running
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "alive", "service": "AI Engine"}
    )


@router.get("/ready")
async def readiness():
    """
    Readiness probe - indicates if service is ready for traffic
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready"}
    )
