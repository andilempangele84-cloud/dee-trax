#!/usr/bin/env python3
"""
Global Exception Handler Middleware

Handles all unhandled exceptions and returns consistent error responses.
"""

import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from config.environment import settings


class GlobalExceptionHandler:
    """
    Global exception handler for all unhandled exceptions
    """
    
    def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle exceptions and return appropriate response
        """
        
        # Log the exception
        error_id = self._generate_error_id()
        logger.error(
            f"Unhandled Exception [ID: {error_id}]: {str(exc)}\n{traceback.format_exc()}"
        )
        
        # Determine status code
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        if isinstance(exc, ValueError):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, PermissionError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, FileNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        
        # Build response
        response_body = {
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "error_id": error_id,
        }
        
        if settings.DEBUG:
            response_body["traceback"] = traceback.format_exc()
            response_body["type"] = type(exc).__name__
        
        return JSONResponse(
            status_code=status_code,
            content=response_body,
        )
    
    @staticmethod
    def _generate_error_id() -> str:
        """Generate unique error ID for tracking"""
        import uuid
        return str(uuid.uuid4())[:8].upper()
