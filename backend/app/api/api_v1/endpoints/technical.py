from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime, timedelta

from app.models.schemas import (
    TechnicalAnalysis, 
    TechnicalIndicator, 
    APIResponse, 
    TimeFrame
)
from app.services.technical_service import TechnicalService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{symbol}", response_model=TechnicalAnalysis)
async def get_technical_analysis(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    indicators: Optional[List[str]] = Query(None),
    technical_service: TechnicalService = Depends()
):
    """
    Get comprehensive technical analysis for a stock symbol
    """
    try:
        logger.info("Getting technical analysis", symbol=symbol, timeframe=timeframe)
        
        analysis = await technical_service.analyze_technical(
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators
        )
        
        return analysis
        
    except Exception as e:
        logger.error("Error getting technical analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/indicators", response_model=List[TechnicalIndicator])
async def get_technical_indicators(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    period: int = Query(14, ge=1, le=200),
    technical_service: TechnicalService = Depends()
):
    """
    Get specific technical indicators for a stock symbol
    """
    try:
        logger.info("Getting technical indicators", symbol=symbol, timeframe=timeframe)
        
        indicators = await technical_service.calculate_indicators(
            symbol=symbol,
            timeframe=timeframe,
            period=period
        )
        
        return indicators
        
    except Exception as e:
        logger.error("Error getting technical indicators", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/signals", response_model=List[dict])
async def get_trading_signals(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    signal_types: Optional[List[str]] = Query(None),
    technical_service: TechnicalService = Depends()
):
    """
    Get trading signals based on technical analysis
    """
    try:
        logger.info("Getting trading signals", symbol=symbol, timeframe=timeframe)
        
        signals = await technical_service.generate_trading_signals(
            symbol=symbol,
            timeframe=timeframe,
            signal_types=signal_types
        )
        
        return signals
        
    except Exception as e:
        logger.error("Error getting trading signals", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/support-resistance", response_model=dict)
async def get_support_resistance_levels(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    lookback_periods: int = Query(50, ge=10, le=200),
    technical_service: TechnicalService = Depends()
):
    """
    Get support and resistance levels for a stock symbol
    """
    try:
        logger.info("Getting support/resistance levels", symbol=symbol, timeframe=timeframe)
        
        levels = await technical_service.calculate_support_resistance(
            symbol=symbol,
            timeframe=timeframe,
            lookback_periods=lookback_periods
        )
        
        return levels
        
    except Exception as e:
        logger.error("Error getting support/resistance levels", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/volatility", response_model=dict)
async def get_volatility_analysis(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    period: int = Query(20, ge=5, le=100),
    technical_service: TechnicalService = Depends()
):
    """
    Get volatility analysis for a stock symbol
    """
    try:
        logger.info("Getting volatility analysis", symbol=symbol, timeframe=timeframe)
        
        volatility = await technical_service.analyze_volatility(
            symbol=symbol,
            timeframe=timeframe,
            period=period
        )
        
        return volatility
        
    except Exception as e:
        logger.error("Error getting volatility analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/pattern-recognition", response_model=List[dict])
async def get_chart_patterns(
    symbol: str,
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    pattern_types: Optional[List[str]] = Query(None),
    technical_service: TechnicalService = Depends()
):
    """
    Get identified chart patterns for a stock symbol
    """
    try:
        logger.info("Getting chart patterns", symbol=symbol, timeframe=timeframe)
        
        patterns = await technical_service.identify_chart_patterns(
            symbol=symbol,
            timeframe=timeframe,
            pattern_types=pattern_types
        )
        
        return patterns
        
    except Exception as e:
        logger.error("Error getting chart patterns", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[TechnicalAnalysis])
async def bulk_technical_analysis(
    symbols: List[str],
    timeframe: TimeFrame = TimeFrame.ONE_DAY,
    technical_service: TechnicalService = Depends()
):
    """
    Get technical analysis for multiple stock symbols
    """
    try:
        logger.info("Bulk technical analysis", symbols=symbols, timeframe=timeframe)
        
        if len(symbols) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 symbols allowed")
        
        analyses = await technical_service.bulk_technical_analysis(
            symbols=symbols,
            timeframe=timeframe
        )
        
        return analyses
        
    except Exception as e:
        logger.error("Error in bulk technical analysis", symbols=symbols, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))