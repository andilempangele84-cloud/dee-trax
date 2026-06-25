#!/usr/bin/env python3
"""
Authentication Middleware

Handles JWT token validation and user context injection.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from loguru import logger
from config.environment import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication
    """
    
    EXCLUDED_PATHS = {"/", "/docs", "/redoc", "/openapi.json", "/api/v1/health"}
    
    async def dispatch(self, request: Request, call_next):
        """
        Process incoming request for authentication
        """
        
        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS or request.url.path.startswith("/api/v1/health"):
            return await call_next(request)
        
        # Skip for non-protected routes
        if not any(prefix in request.url.path for prefix in ["/api/v1/llm", "/api/v1/agents", "/api/v1/nlp", "/api/v1/embeddings"]):
            return await call_next(request)
        
        # Extract token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing authorization header"},
            )
        
        try:
            scheme, token = auth_header.split(" ")
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
            
            # Verify token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            
            # Add user context to request
            request.state.user_id = payload.get("sub")
            request.state.user = payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Token has expired"},
            )
        except (jwt.InvalidTokenError, ValueError) as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid token"},
            )
        
        return await call_next(request)
