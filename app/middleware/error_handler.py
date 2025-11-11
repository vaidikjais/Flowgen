"""
Error Handler Middleware

Global error handling middleware that catches and formats exceptions
into consistent error responses.
"""
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import (
    FlowgenException,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling.
    
    Catches exceptions and converts them to appropriate HTTP responses
    with consistent error format.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request with error handling."""
        
        try:
            response = await call_next(request)
            return response
            
        except ResourceNotFoundError as e:
            logger.warning(f"Resource not found: {e.message}")
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Not Found",
                    "detail": e.message,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e.message}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "detail": e.message,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e.message}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate Limit Exceeded",
                    "detail": e.message,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except FlowgenException as e:
            logger.error(f"Application error: {e.message}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": e.message,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )

