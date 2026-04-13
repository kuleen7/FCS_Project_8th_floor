"""
Main FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging
from collections import defaultdict, deque

from .config import settings
from .database import init_db
from .middleware.audit_middleware import AuditMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
REQUEST_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 120
AUTH_MAX_REQUESTS_PER_WINDOW = 20
request_tracker = defaultdict(deque)
SUSPICIOUS_PATTERNS = [
    "<script",
    "' or 1=1",
    "union select",
    "../",
    "javascript:",
]
CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Middleware
app.add_middleware(AuditMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Basic rate limiting
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{request.url.path}"
    now = time.time()
    window = request_tracker[key]
    while window and now - window[0] > REQUEST_WINDOW_SECONDS:
        window.popleft()
    limit = AUTH_MAX_REQUESTS_PER_WINDOW if request.url.path.startswith("/api/auth") else MAX_REQUESTS_PER_WINDOW
    if len(window) >= limit:
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    window.append(now)

    # Basic request payload attack pattern filter
    query = str(request.url.query).lower()
    if any(pattern in query for pattern in SUSPICIOUS_PATTERNS):
        return JSONResponse(status_code=400, content={"detail": "Suspicious request blocked"})

    # Basic CSRF/origin validation for browser-originated state-changing requests.
    if request.url.path.startswith("/api/") and request.method in CSRF_PROTECTED_METHODS:
        origin = request.headers.get("origin")
        sec_fetch_site = request.headers.get("sec-fetch-site", "")
        if origin:
            allowed_origins = set(settings.CORS_ORIGINS or [])
            if origin not in allowed_origins:
                return JSONResponse(status_code=403, content={"detail": "Blocked by CSRF origin policy"})
        # If browser says cross-site on a state-changing call, block.
        if sec_fetch_site.lower() == "cross-site":
            return JSONResponse(status_code=403, content={"detail": "Cross-site state-changing request blocked"})
    
    # Process request
    response = await call_next(request)

    # Security response headers for web attack defense
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Cache-Control"] = "no-store"
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - Time: {process_time:.2f}s")
    
    return response


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "https": settings.USE_SSL
    }


# Root endpoint
@app.get("/api/")
async def root():
    """Root API endpoint"""
    return {
        "message": "Welcome to Secure Job Search Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    logger.info(f"HTTPS enabled: {settings.USE_SSL}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("Shutting down application")


# Import and include routers
from .api import auth, users, admin, companies, jobs, applications, messages, audit, profile, april, social

app.include_router(auth.router)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# March Milestone 3 routers
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(april.router, prefix="/api/april", tags=["April Milestone"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])


if __name__ == "__main__":
    import uvicorn
    
    # Run with HTTPS if enabled
    if settings.USE_SSL:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=settings.SSL_KEY_PATH,
            ssl_certfile=settings.SSL_CERT_PATH,
            reload=settings.DEBUG
        )
    else:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG
        )
