from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime, timedelta

from app.models.schemas import (
    SentimentAnalysis, 
    SentimentScore, 
    APIResponse, 
    TimeFrame
)
from app.services.sentiment_service import SentimentService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{symbol}", response_model=SentimentAnalysis)
async def get_sentiment_analysis(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    include_news: bool = True,
    include_social: bool = True,
    sentiment_service: SentimentService = Depends()
):
    """
    Get comprehensive sentiment analysis for a stock symbol
    """
    try:
        logger.info("Getting sentiment analysis", symbol=symbol, timeframe=timeframe)
        
        analysis = await sentiment_service.analyze_sentiment(
            symbol=symbol,
            timeframe=timeframe,
            include_news=include_news,
            include_social=include_social
        )
        
        return analysis
        
    except Exception as e:
        logger.error("Error getting sentiment analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/trend", response_model=List[dict])
async def get_sentiment_trend(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    sentiment_service: SentimentService = Depends()
):
    """
    Get sentiment trend over time for a stock symbol
    """
    try:
        logger.info("Getting sentiment trend", symbol=symbol, days=days)
        
        trend = await sentiment_service.get_sentiment_trend(
            symbol=symbol,
            days=days
        )
        
        return trend
        
    except Exception as e:
        logger.error("Error getting sentiment trend", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/news", response_model=List[dict])
async def get_news_sentiment(
    symbol: str,
    limit: int = Query(50, ge=1, le=200),
    sentiment_service: SentimentService = Depends()
):
    """
    Get news articles with sentiment analysis for a stock symbol
    """
    try:
        logger.info("Getting news sentiment", symbol=symbol, limit=limit)
        
        news = await sentiment_service.get_news_with_sentiment(
            symbol=symbol,
            limit=limit
        )
        
        return news
        
    except Exception as e:
        logger.error("Error getting news sentiment", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/social", response_model=List[dict])
async def get_social_sentiment(
    symbol: str,
    platform: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    sentiment_service: SentimentService = Depends()
):
    """
    Get social media posts with sentiment analysis for a stock symbol
    """
    try:
        logger.info("Getting social sentiment", symbol=symbol, platform=platform, limit=limit)
        
        posts = await sentiment_service.get_social_media_sentiment(
            symbol=symbol,
            platform=platform,
            limit=limit
        )
        
        return posts
        
    except Exception as e:
        logger.error("Error getting social sentiment", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[SentimentAnalysis])
async def bulk_sentiment_analysis(
    symbols: List[str],
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    sentiment_service: SentimentService = Depends()
):
    """
    Get sentiment analysis for multiple stock symbols
    """
    try:
        logger.info("Bulk sentiment analysis", symbols=symbols, timeframe=timeframe)
        
        if len(symbols) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 symbols allowed")
        
        analyses = await sentiment_service.bulk_sentiment_analysis(
            symbols=symbols,
            timeframe=timeframe
        )
        
        return analyses
        
    except Exception as e:
        logger.error("Error in bulk sentiment analysis", symbols=symbols, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/overview", response_model=dict)
async def get_market_sentiment_overview(
    sector: Optional[str] = Query(None),
    sentiment_service: SentimentService = Depends()
):
    """
    Get overall market sentiment overview
    """
    try:
        logger.info("Getting market sentiment overview", sector=sector)
        
        overview = await sentiment_service.get_market_sentiment_overview(sector=sector)
        
        return overview
        
    except Exception as e:
        logger.error("Error getting market sentiment overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))