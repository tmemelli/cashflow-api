"""
Main application module.

This is the entry point of the FastAPI application.
It creates the app instance, configures middleware, and includes all routers.

To run the application:
    uvicorn app.main:app --reload
    
Then access:
    - API: http://localhost:8000
    - Interactive docs: http://localhost:8000/docs
    - Alternative docs: http://localhost:8000/redoc
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.v1.api import api_router
from app.core.config import settings
from fastapi.openapi.utils import get_openapi
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing cash flow with multiple authentication methods.",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# Create database tables on startup
@app.on_event("startup")
def on_startup():
    """
    Create all database tables when the application starts.
    
    This will create tables for all models imported in app/db/base.py
    If tables already exist, this operation is safe and won't modify them.
    """
    Base.metadata.create_all(bind=engine)


# Custom OpenAPI schema with multiple auth methods
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="CashFlow API with multiple authentication methods",
        routes=app.routes,
    )
    
    # Add both authentication schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{settings.API_V1_STR}/auth/login",
                    "scopes": {}
                }
            }
        },
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Middleware to prevent caching (helps with Swagger UI token issues)
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """
    Root endpoint.
    
    Welcome message for the API.
    
    Returns:
        dict: Welcome message with API info
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }