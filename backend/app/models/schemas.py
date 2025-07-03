from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums
class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class TimeFrame(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class MarketSector(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    ENERGY = "energy"
    CONSUMER_DISCRETIONARY = "consumer_discretionary"
    CONSUMER_STAPLES = "consumer_staples"
    INDUSTRIALS = "industrials"
    MATERIALS = "materials"
    REAL_ESTATE = "real_estate"
    UTILITIES = "utilities"
    TELECOMMUNICATIONS = "telecommunications"


# Base Models
class StockInfo(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[MarketSector] = None
    market_cap: Optional[float] = None
    price: Optional[float] = None
    currency: str = "USD"


class TimeSeriesData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None


# Sentiment Models
class SentimentScore(BaseModel):
    label: SentimentLabel
    score: float = Field(..., ge=0, le=1, description="Confidence score between 0 and 1")
    compound_score: Optional[float] = Field(None, ge=-1, le=1)


class NewsArticle(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    url: Optional[str] = None
    source: str
    published_at: datetime
    symbols: List[str] = []
    sentiment: Optional[SentimentScore] = None


class SocialMediaPost(BaseModel):
    id: str
    platform: str  # twitter, reddit, etc.
    content: str
    author: Optional[str] = None
    posted_at: datetime
    symbols: List[str] = []
    engagement_metrics: Dict[str, int] = {}  # likes, shares, comments
    sentiment: Optional[SentimentScore] = None


class SentimentAnalysis(BaseModel):
    symbol: str
    overall_sentiment: SentimentScore
    news_sentiment: Optional[SentimentScore] = None
    social_sentiment: Optional[SentimentScore] = None
    sentiment_trend: List[Dict[str, Any]] = []
    analyzed_at: datetime
    sample_size: int


# Technical Analysis Models
class TechnicalIndicator(BaseModel):
    name: str
    value: float
    signal: Optional[str] = None  # buy, sell, hold
    timestamp: datetime


class TechnicalAnalysis(BaseModel):
    symbol: str
    timeframe: TimeFrame
    indicators: List[TechnicalIndicator]
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    trend_direction: Optional[str] = None
    volatility: Optional[float] = None
    analyzed_at: datetime


# Fundamental Analysis Models
class FinancialMetrics(BaseModel):
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    earnings_per_share: Optional[float] = None
    price_to_earnings: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None


class FundamentalAnalysis(BaseModel):
    symbol: str
    financial_metrics: FinancialMetrics
    valuation_score: Optional[float] = None
    financial_health_score: Optional[float] = None
    growth_score: Optional[float] = None
    analyzed_at: datetime


# Prediction Models
class PredictionFeatures(BaseModel):
    sentiment_features: Dict[str, float] = {}
    technical_features: Dict[str, float] = {}
    fundamental_features: Dict[str, float] = {}
    macro_features: Dict[str, float] = {}


class PredictionResult(BaseModel):
    symbol: str
    prediction_type: str  # price, direction, volatility
    predicted_value: float
    confidence: float = Field(..., ge=0, le=1)
    time_horizon: str  # 1d, 1w, 1m, 3m
    features_used: PredictionFeatures
    model_version: str
    predicted_at: datetime


class ExplainabilityResult(BaseModel):
    prediction_id: str
    feature_importance: Dict[str, float]
    shap_values: Dict[str, float]
    lime_explanation: Optional[Dict[str, Any]] = None
    top_contributing_factors: List[Dict[str, Any]]
    explanation_text: str


# Market Insights Models
class MarketInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    severity: str  # low, medium, high
    affected_symbols: List[str] = []
    confidence: float = Field(..., ge=0, le=1)
    generated_at: datetime
    supporting_evidence: List[Dict[str, Any]] = []


class PortfolioAnalysis(BaseModel):
    portfolio_id: str
    symbols: List[str]
    total_value: float
    daily_return: float
    volatility: float
    beta: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    risk_score: float = Field(..., ge=0, le=10)
    sentiment_exposure: Dict[str, float] = {}
    sector_allocation: Dict[str, float] = {}
    analyzed_at: datetime


# Real-time Data Models
class RealTimeUpdate(BaseModel):
    update_type: str  # price, sentiment, news, alert
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, urgent


class AlertRule(BaseModel):
    rule_id: str
    user_id: str
    symbol: str
    condition: str  # price_change, sentiment_change, volume_spike, etc.
    threshold: float
    timeframe: TimeFrame
    is_active: bool = True
    created_at: datetime


# API Response Models
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Request completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 50
    pages: int


# Request Models
class StockAnalysisRequest(BaseModel):
    symbol: str
    timeframe: TimeFrame = TimeFrame.ONE_DAY
    include_sentiment: bool = True
    include_technical: bool = True
    include_fundamental: bool = True


class PredictionRequest(BaseModel):
    symbol: str
    prediction_type: str = "price"
    time_horizon: str = "1d"
    include_explainability: bool = False


class BulkAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., max_items=100)
    analysis_types: List[str] = ["sentiment", "technical", "fundamental"]
    timeframe: TimeFrame = TimeFrame.ONE_DAY


# Websocket Models
class WebSocketMessage(BaseModel):
    type: str  # subscribe, unsubscribe, data, error
    topic: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    client_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)