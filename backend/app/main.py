"""FastAPI application entry point"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.logging_config import setup_logging
from app.rate_limit import limiter
from app.api.routes import auth, frames, metrics, alerts, comments, users, movements, risk, posture
import logging
import time

# Setup logging
log_level = "DEBUG" if settings.DEBUG else "INFO"
setup_logging(log_level=log_level, log_file="logs/app.log")
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Pressure ulcer prevention application with real-time monitoring and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger.info(f"Starting {settings.APP_NAME} in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode")

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request logging middleware


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information"""
    start_time = time.time()

    # Log request
    logger.info(
        "request_started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    # Log response
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(duration_ms)

    return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Graphene Trace API is running",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(frames.router, prefix="/api/frames", tags=["frames"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(movements.router, prefix="/api/movements", tags=["movements"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(posture.router, prefix="/api/posture", tags=["posture"])
# app.include_router(groups.router, prefix="/api/groups", tags=["groups"])  # To be implemented
