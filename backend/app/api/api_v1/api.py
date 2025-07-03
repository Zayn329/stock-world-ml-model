from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    sentiment,
    technical,
    fundamental,
    predictions,
    stocks,
    insights,
    explainability
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    sentiment.router, 
    prefix="/sentiment", 
    tags=["sentiment"]
)

api_router.include_router(
    technical.router, 
    prefix="/technical", 
    tags=["technical"]
)

api_router.include_router(
    fundamental.router, 
    prefix="/fundamental", 
    tags=["fundamental"]
)

api_router.include_router(
    predictions.router, 
    prefix="/predictions", 
    tags=["predictions"]
)

api_router.include_router(
    stocks.router, 
    prefix="/stocks", 
    tags=["stocks"]
)

api_router.include_router(
    insights.router, 
    prefix="/insights", 
    tags=["insights"]
)

api_router.include_router(
    explainability.router, 
    prefix="/explainability", 
    tags=["explainability"]
)