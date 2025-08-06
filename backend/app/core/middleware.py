from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
import uuid
from typing import Callable

from app.core.sentry import set_request_context, capture_custom_error, add_breadcrumb
import sentry_sdk


class SentryMiddleware:
    """Middleware for enhanced Sentry integration."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing the request
        start_time = time.time()
        
        # Extract request info
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        # Set Sentry context
        with sentry_sdk.configure_scope() as sentry_scope:
            sentry_scope.set_tag("request_id", request_id)
            sentry_scope.set_tag("method", method)
            sentry_scope.set_tag("path", path)
            
            # Add breadcrumb for request start
            add_breadcrumb(
                message=f"Request started: {method} {path}",
                category="request",
                level="info",
                data={"request_id": request_id}
            )
        
        try:
            await self.app(scope, receive, send)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Add success breadcrumb
            add_breadcrumb(
                message=f"Request completed: {method} {path}",
                category="request",
                level="info",
                data={
                    "request_id": request_id,
                    "duration": f"{duration:.3f}s"
                }
            )
            
        except Exception as e:
            # Calculate request duration for error case
            duration = time.time() - start_time
            
            # Capture error with context
            capture_custom_error(e, {
                "request_id": request_id,
                "method": method,
                "path": path,
                "duration": f"{duration:.3f}s"
            })
            
            # Log the error
            logging.error(f"Request {request_id} failed: {str(e)}")
            
            # Re-raise the exception
            raise


async def log_requests_middleware(request: Request, call_next):
    """Middleware to log all requests with timing."""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Add request info to Sentry scope
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("request_id", request_id)
        scope.set_extra("request_url", str(request.url))
        scope.set_extra("request_method", request.method)
        scope.set_extra("user_agent", request.headers.get("user-agent", ""))
    
    # Log request start
    logging.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add timing to response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log successful request
        logging.info(
            f"Request {request_id} completed: "
            f"{response.status_code} in {process_time:.3f}s"
        )
        
        # Add performance breadcrumb
        add_breadcrumb(
            message="Request processing completed",
            category="performance",
            level="info",
            data={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time": f"{process_time:.3f}s"
            }
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        
        # Log error
        logging.error(
            f"Request {request_id} failed: {str(e)} "
            f"after {process_time:.3f}s"
        )
        
        # Capture error with detailed context
        capture_custom_error(e, {
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "processing_time": f"{process_time:.3f}s",
            "headers": dict(request.headers),
        })
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id
            },
            headers={"X-Request-ID": request_id}
        )
