import logging
import os
from typing import Optional, Any, Dict

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry SDK not available - error monitoring disabled")

from app.core.config import settings


def init_sentry() -> None:
    """Initialize Sentry error monitoring and performance tracking."""
    
    if not SENTRY_AVAILABLE:
        logging.info("Sentry SDK not available, skipping initialization")
        return
    
    if not settings.SENTRY_DSN:
        logging.info("Sentry DSN not configured, skipping Sentry initialization")
        return
    
    # Determine environment and sampling rates
    environment = settings.SENTRY_ENVIRONMENT or os.getenv("ENVIRONMENT", "development")
    
    # Adjust sampling rates based on environment
    if environment == "production":
        traces_sample_rate = settings.SENTRY_TRACES_SAMPLE_RATE or 0.1
        sample_rate = 1.0  # Capture all errors in production
    else:
        traces_sample_rate = 1.0  # Full tracing in development
        sample_rate = 1.0
    
    # Configure Sentry integrations
    integrations = [
        # FastAPI integration for automatic request tracking
        FastApiIntegration(
            transaction_style="endpoint",
            failed_request_status_codes=[400, 401, 403, 404, 405, 500, 502, 503, 504],
        ),
        
        # SQLAlchemy integration for database query tracking
        SqlalchemyIntegration(),
        
        # Async integration for proper async handling
        AsyncioIntegration(),
        
        # Logging integration
        LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        ),
    ]
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=environment,
        integrations=integrations,
        
        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        
        # Error sampling
        sample_rate=sample_rate,
        
        # Additional configuration
        attach_stacktrace=True,
        send_default_pii=True,  # Add data like request headers and IP for users (as per Sentry docs)
        
        # Custom tags
        before_send=before_send_filter,
        
        # Performance configuration
        profiles_sample_rate=0.1 if environment == "production" else 1.0,
    )
    
    logging.info(f"Sentry initialized for environment: {environment}")


def before_send_filter(event, hint):
    """Filter and modify events before sending to Sentry."""
    
    # Add custom tags
    if 'tags' not in event:
        event['tags'] = {}
    
    event['tags']['service'] = 'quickvendor-backend'
    event['tags']['component'] = 'api'
    
    # Filter out certain exceptions in development
    if settings.SENTRY_ENVIRONMENT == "development":
        # Don't send validation errors in development
        if 'exception' in event:
            for exception in event['exception']['values']:
                if 'ValidationError' in exception.get('type', ''):
                    return None
    
    return event


def set_user_context(user_id: str, email: Optional[str] = None) -> None:
    """Set user context for Sentry tracking."""
    if not SENTRY_AVAILABLE:
        return
    
    with sentry_sdk.configure_scope() as scope:
        scope.set_user({
            "id": user_id,
            "email": email,
        })


def set_request_context(path: str, method: str, user_id: Optional[str] = None) -> None:
    """Set request context for better error tracking."""
    if not SENTRY_AVAILABLE:
        return
    
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("endpoint", f"{method} {path}")
        if user_id:
            scope.set_tag("user_id", user_id)


def capture_custom_error(error: Exception, context: dict = None) -> Optional[str]:
    """Capture a custom error with additional context."""
    if not SENTRY_AVAILABLE:
        logging.error(f"Error (Sentry unavailable): {error}", exc_info=True)
        return None
    
    with sentry_sdk.configure_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        
        return sentry_sdk.capture_exception(error)


def capture_message_with_context(message: str, level: str = "info", context: dict = None) -> Optional[str]:
    """Capture a message with additional context."""
    if not SENTRY_AVAILABLE:
        logging.log(getattr(logging, level.upper(), logging.INFO), f"Sentry message: {message}")
        return None
    
    with sentry_sdk.configure_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_extra(key, value)
        
        return sentry_sdk.capture_message(message, level=level)


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: dict = None) -> None:
    """Add a breadcrumb for better error context."""
    if not SENTRY_AVAILABLE:
        return
    
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
