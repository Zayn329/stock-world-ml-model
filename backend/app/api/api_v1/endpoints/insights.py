from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime

from app.models.schemas import (
    MarketInsight, 
    PortfolioAnalysis, 
    APIResponse
)
from app.services.insights_service import InsightsService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/market", response_model=List[MarketInsight])
async def get_market_insights(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    insights_service: InsightsService = Depends()
):
    """
    Get general market insights and analysis
    """
    try:
        logger.info("Getting market insights", limit=limit, severity=severity)
        
        insights = await insights_service.get_market_insights(limit, severity)
        
        return insights
        
    except Exception as e:
        logger.error("Error getting market insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=List[MarketInsight])
async def get_stock_insights(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    insights_service: InsightsService = Depends()
):
    """
    Get insights specific to a stock symbol
    """
    try:
        logger.info("Getting stock insights", symbol=symbol, limit=limit)
        
        insights = await insights_service.get_stock_insights(symbol, limit)
        
        return insights
        
    except Exception as e:
        logger.error("Error getting stock insights", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector/{sector}", response_model=List[MarketInsight])
async def get_sector_insights(
    sector: str,
    limit: int = Query(15, ge=1, le=50),
    insights_service: InsightsService = Depends()
):
    """
    Get insights for a specific market sector
    """
    try:
        logger.info("Getting sector insights", sector=sector, limit=limit)
        
        insights = await insights_service.get_sector_insights(sector, limit)
        
        return insights
        
    except Exception as e:
        logger.error("Error getting sector insights", sector=sector, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities/growth", response_model=List[dict])
async def get_growth_opportunities(
    limit: int = Query(20, ge=1, le=100),
    min_confidence: float = Query(0.7, ge=0.0, le=1.0),
    insights_service: InsightsService = Depends()
):
    """
    Get identified growth opportunities across the market
    """
    try:
        logger.info("Getting growth opportunities", limit=limit, min_confidence=min_confidence)
        
        opportunities = await insights_service.identify_growth_opportunities(limit, min_confidence)
        
        return opportunities
        
    except Exception as e:
        logger.error("Error getting growth opportunities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities/value", response_model=List[dict])
async def get_value_opportunities(
    limit: int = Query(20, ge=1, le=100),
    min_confidence: float = Query(0.7, ge=0.0, le=1.0),
    insights_service: InsightsService = Depends()
):
    """
    Get identified value investing opportunities
    """
    try:
        logger.info("Getting value opportunities", limit=limit, min_confidence=min_confidence)
        
        opportunities = await insights_service.identify_value_opportunities(limit, min_confidence)
        
        return opportunities
        
    except Exception as e:
        logger.error("Error getting value opportunities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risks/market", response_model=List[dict])
async def get_market_risks(
    limit: int = Query(15, ge=1, le=50),
    insights_service: InsightsService = Depends()
):
    """
    Get identified market risks and warning signals
    """
    try:
        logger.info("Getting market risks", limit=limit)
        
        risks = await insights_service.identify_market_risks(limit)
        
        return risks
        
    except Exception as e:
        logger.error("Error getting market risks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/analyze", response_model=PortfolioAnalysis)
async def analyze_portfolio(
    symbols: List[str],
    weights: Optional[List[float]] = None,
    insights_service: InsightsService = Depends()
):
    """
    Analyze a portfolio of stocks for risk, diversification, and insights
    """
    try:
        logger.info("Analyzing portfolio", symbols=symbols)
        
        if len(symbols) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 symbols allowed")
        
        if weights and len(weights) != len(symbols):
            raise HTTPException(status_code=400, detail="Weights list must match symbols list length")
        
        analysis = await insights_service.analyze_portfolio(symbols, weights)
        
        return analysis
        
    except Exception as e:
        logger.error("Error analyzing portfolio", symbols=symbols, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/emerging", response_model=List[dict])
async def get_emerging_trends(
    limit: int = Query(10, ge=1, le=50),
    timeframe: str = Query("1w", regex="^(1d|1w|1m|3m)$"),
    insights_service: InsightsService = Depends()
):
    """
    Get emerging market trends and themes
    """
    try:
        logger.info("Getting emerging trends", limit=limit, timeframe=timeframe)
        
        trends = await insights_service.identify_emerging_trends(limit, timeframe)
        
        return trends
        
    except Exception as e:
        logger.error("Error getting emerging trends", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlations/{symbol}", response_model=dict)
async def get_correlation_analysis(
    symbol: str,
    insights_service: InsightsService = Depends()
):
    """
    Get correlation analysis for a stock with market indices and other stocks
    """
    try:
        logger.info("Getting correlation analysis", symbol=symbol)
        
        correlations = await insights_service.analyze_correlations(symbol)
        
        return correlations
        
    except Exception as e:
        logger.error("Error getting correlation analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", response_model=List[dict])
async def get_market_anomalies(
    limit: int = Query(20, ge=1, le=100),
    confidence_threshold: float = Query(0.8, ge=0.5, le=1.0),
    insights_service: InsightsService = Depends()
):
    """
    Get detected market anomalies and unusual patterns
    """
    try:
        logger.info("Getting market anomalies", limit=limit, confidence_threshold=confidence_threshold)
        
        anomalies = await insights_service.detect_market_anomalies(limit, confidence_threshold)
        
        return anomalies
        
    except Exception as e:
        logger.error("Error getting market anomalies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))