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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


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