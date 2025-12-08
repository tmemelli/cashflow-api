"""
API v1 router module.

This module aggregates all API v1 endpoints into a single router.
It includes routers from different endpoint modules (auth, transactions, etc).

The main API router is then included in the application with the
/api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, transactions, reports

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Category endpoints
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"]
)

# Transaction endpoints
api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"]
)

# Reports endpoints
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)