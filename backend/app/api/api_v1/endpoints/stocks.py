from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime, timedelta

from app.models.schemas import (
    StockInfo, 
    TimeSeriesData, 
    TimeFrame, 
    APIResponse
)
from app.services.stock_service import StockService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{symbol}/info", response_model=StockInfo)
async def get_stock_info(
    symbol: str,
    stock_service: StockService = Depends()
):
    """
    Get basic information about a stock
    """
    try:
        logger.info("Getting stock info", symbol=symbol)
        
        stock_info = await stock_service.get_stock_info(symbol)
        
        if not stock_info:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        return stock_info
        
    except Exception as e:
        logger.error("Error getting stock info", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/price", response_model=dict)
async def get_current_price(
    symbol: str,
    stock_service: StockService = Depends()
):
    """
    Get current price and basic metrics for a stock
    """
    try:
        logger.info("Getting current price", symbol=symbol)
        
        price_data = await stock_service.get_current_price(symbol)
        
        return price_data
        
    except Exception as e:
        logger.error("Error getting current price", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history", response_model=List[TimeSeriesData])
async def get_price_history(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$"),
    stock_service: StockService = Depends()
):
    """
    Get historical price data for a stock
    """
    try:
        logger.info("Getting price history", symbol=symbol, timeframe=timeframe, period=period)
        
        history = await stock_service.get_price_history(
            symbol=symbol,
            timeframe=timeframe,
            period=period
        )
        
        return history
        
    except Exception as e:
        logger.error("Error getting price history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[StockInfo])
async def search_stocks(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    stock_service: StockService = Depends()
):
    """
    Search for stocks by symbol or company name
    """
    try:
        logger.info("Searching stocks", query=query, limit=limit)
        
        results = await stock_service.search_stocks(query, limit)
        
        return results
        
    except Exception as e:
        logger.error("Error searching stocks", query=query, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending", response_model=List[dict])
async def get_trending_stocks(
    limit: int = Query(50, ge=1, le=100),
    timeframe: str = Query("1d", regex="^(1h|1d|1w)$"),
    stock_service: StockService = Depends()
):
    """
    Get trending stocks based on volume, price movement, and sentiment
    """
    try:
        logger.info("Getting trending stocks", limit=limit, timeframe=timeframe)
        
        trending = await stock_service.get_trending_stocks(limit, timeframe)
        
        return trending
        
    except Exception as e:
        logger.error("Error getting trending stocks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sectors", response_model=List[dict])
async def get_sector_performance(
    stock_service: StockService = Depends()
):
    """
    Get performance overview by market sector
    """
    try:
        logger.info("Getting sector performance")
        
        sectors = await stock_service.get_sector_performance()
        
        return sectors
        
    except Exception as e:
        logger.error("Error getting sector performance", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/peers", response_model=List[StockInfo])
async def get_peer_stocks(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    stock_service: StockService = Depends()
):
    """
    Get peer stocks in the same sector/industry
    """
    try:
        logger.info("Getting peer stocks", symbol=symbol, limit=limit)
        
        peers = await stock_service.get_peer_stocks(symbol, limit)
        
        return peers
        
    except Exception as e:
        logger.error("Error getting peer stocks", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/dividends", response_model=List[dict])
async def get_dividend_history(
    symbol: str,
    years: int = Query(5, ge=1, le=20),
    stock_service: StockService = Depends()
):
    """
    Get dividend history for a stock
    """
    try:
        logger.info("Getting dividend history", symbol=symbol, years=years)
        
        dividends = await stock_service.get_dividend_history(symbol, years)
        
        return dividends
        
    except Exception as e:
        logger.error("Error getting dividend history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/earnings", response_model=List[dict])
async def get_earnings_history(
    symbol: str,
    quarters: int = Query(12, ge=1, le=40),
    stock_service: StockService = Depends()
):
    """
    Get earnings history for a stock
    """
    try:
        logger.info("Getting earnings history", symbol=symbol, quarters=quarters)
        
        earnings = await stock_service.get_earnings_history(symbol, quarters)
        
        return earnings
        
    except Exception as e:
        logger.error("Error getting earnings history", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))