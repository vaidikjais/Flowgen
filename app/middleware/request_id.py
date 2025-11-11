"""
Request ID Middleware

Adds unique request ID to all incoming requests for tracking
and logging purposes.
"""
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import set_request_id, clear_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to all requests.
    
    The request ID is:
    1. Generated as a UUID for each request
    2. Added to response headers as X-Request-ID
    3. Set in logging context for all logs during request
    4. Cleared after request completes
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Process request with unique request ID."""
        
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set in logging context
        set_request_id(request_id)
        
        # Add to request state for access in route handlers
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        finally:
            # Clear request ID from context
            clear_request_id()

