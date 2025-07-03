from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime

from app.models.schemas import (
    FundamentalAnalysis, 
    FinancialMetrics, 
    APIResponse
)
from app.services.fundamental_service import FundamentalService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{symbol}", response_model=FundamentalAnalysis)
async def get_fundamental_analysis(
    symbol: str,
    fundamental_service: FundamentalService = Depends()
):
    """
    Get comprehensive fundamental analysis for a stock
    """
    try:
        logger.info("Getting fundamental analysis", symbol=symbol)
        
        analysis = await fundamental_service.analyze_fundamentals(symbol)
        
        return analysis
        
    except Exception as e:
        logger.error("Error getting fundamental analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/metrics", response_model=FinancialMetrics)
async def get_financial_metrics(
    symbol: str,
    period: str = Query("annual", regex="^(annual|quarterly)$"),
    fundamental_service: FundamentalService = Depends()
):
    """
    Get key financial metrics for a stock
    """
    try:
        logger.info("Getting financial metrics", symbol=symbol, period=period)
        
        metrics = await fundamental_service.get_financial_metrics(symbol, period)
        
        return metrics
        
    except Exception as e:
        logger.error("Error getting financial metrics", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/ratios", response_model=dict)
async def get_financial_ratios(
    symbol: str,
    fundamental_service: FundamentalService = Depends()
):
    """
    Get comprehensive financial ratios for a stock
    """
    try:
        logger.info("Getting financial ratios", symbol=symbol)
        
        ratios = await fundamental_service.calculate_financial_ratios(symbol)
        
        return ratios
        
    except Exception as e:
        logger.error("Error getting financial ratios", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/valuation", response_model=dict)
async def get_valuation_analysis(
    symbol: str,
    fundamental_service: FundamentalService = Depends()
):
    """
    Get valuation analysis including DCF, peer comparison
    """
    try:
        logger.info("Getting valuation analysis", symbol=symbol)
        
        valuation = await fundamental_service.calculate_valuation(symbol)
        
        return valuation
        
    except Exception as e:
        logger.error("Error getting valuation analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/cash-flow", response_model=List[dict])
async def get_cash_flow_statement(
    symbol: str,
    years: int = Query(5, ge=1, le=10),
    fundamental_service: FundamentalService = Depends()
):
    """
    Get cash flow statement data
    """
    try:
        logger.info("Getting cash flow statement", symbol=symbol, years=years)
        
        cash_flow = await fundamental_service.get_cash_flow_statement(symbol, years)
        
        return cash_flow
        
    except Exception as e:
        logger.error("Error getting cash flow statement", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/balance-sheet", response_model=List[dict])
async def get_balance_sheet(
    symbol: str,
    years: int = Query(5, ge=1, le=10),
    fundamental_service: FundamentalService = Depends()
):
    """
    Get balance sheet data
    """
    try:
        logger.info("Getting balance sheet", symbol=symbol, years=years)
        
        balance_sheet = await fundamental_service.get_balance_sheet(symbol, years)
        
        return balance_sheet
        
    except Exception as e:
        logger.error("Error getting balance sheet", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/income-statement", response_model=List[dict])
async def get_income_statement(
    symbol: str,
    years: int = Query(5, ge=1, le=10),
    fundamental_service: FundamentalService = Depends()
):
    """
    Get income statement data
    """
    try:
        logger.info("Getting income statement", symbol=symbol, years=years)
        
        income_statement = await fundamental_service.get_income_statement(symbol, years)
        
        return income_statement
        
    except Exception as e:
        logger.error("Error getting income statement", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/growth", response_model=dict)
async def get_growth_analysis(
    symbol: str,
    fundamental_service: FundamentalService = Depends()
):
    """
    Get growth analysis including revenue, earnings, and margin trends
    """
    try:
        logger.info("Getting growth analysis", symbol=symbol)
        
        growth = await fundamental_service.analyze_growth_trends(symbol)
        
        return growth
        
    except Exception as e:
        logger.error("Error getting growth analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/competitive-analysis", response_model=dict)
async def get_competitive_analysis(
    symbol: str,
    fundamental_service: FundamentalService = Depends()
):
    """
    Get competitive analysis compared to industry peers
    """
    try:
        logger.info("Getting competitive analysis", symbol=symbol)
        
        analysis = await fundamental_service.get_competitive_analysis(symbol)
        
        return analysis
        
    except Exception as e:
        logger.error("Error getting competitive analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[FundamentalAnalysis])
async def bulk_fundamental_analysis(
    symbols: List[str],
    fundamental_service: FundamentalService = Depends()
):
    """
    Get fundamental analysis for multiple stocks
    """
    try:
        logger.info("Bulk fundamental analysis", symbols=symbols)
        
        if len(symbols) > 25:
            raise HTTPException(status_code=400, detail="Maximum 25 symbols allowed")
        
        analyses = await fundamental_service.bulk_fundamental_analysis(symbols)
        
        return analyses
        
    except Exception as e:
        logger.error("Error in bulk fundamental analysis", symbols=symbols, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))