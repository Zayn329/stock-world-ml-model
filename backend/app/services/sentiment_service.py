import asyncio
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime, timedelta
import requests
import json

from app.models.schemas import (
    SentimentAnalysis, SentimentScore, NewsArticle, 
    SocialMediaPost, SentimentLabel, TimeFrame
)
from app.core.config import settings
from app.ml.sentiment.finbert_model import FinBERTSentimentModel

logger = structlog.get_logger(__name__)


class SentimentService:
    """
    Service for sentiment analysis operations
    """
    
    def __init__(self):
        self.finbert_model = None
        self.news_sources = ['newsapi', 'alpha_vantage', 'yahoo_finance']
        self.social_sources = ['twitter', 'reddit']
        self.cache_timeout = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize sentiment service"""
        try:
            # Initialize FinBERT model
            self.finbert_model = FinBERTSentimentModel()
            await self.finbert_model.load_model()
            
            logger.info("Sentiment service initialized successfully")
            
        except Exception as e:
            logger.error("Error initializing sentiment service", error=str(e))
            raise
    
    async def analyze_sentiment(self, symbol: str, timeframe: TimeFrame = TimeFrame.ONE_DAY,
                              include_news: bool = True, include_social: bool = True) -> SentimentAnalysis:
        """
        Perform comprehensive sentiment analysis for a stock symbol
        """
        try:
            logger.info("Analyzing sentiment", symbol=symbol, timeframe=timeframe)
            
            # Initialize results
            news_sentiment = None
            social_sentiment = None
            sentiment_trend = []
            
            # Collect data
            news_data = []
            social_data = []
            
            if include_news:
                news_data = await self._fetch_news_data(symbol, timeframe)
                if news_data:
                    news_sentiment = await self._analyze_news_sentiment(news_data)
            
            if include_social:
                social_data = await self._fetch_social_data(symbol, timeframe)
                if social_data:
                    social_sentiment = await self._analyze_social_sentiment(social_data)
            
            # Calculate overall sentiment
            overall_sentiment = await self._calculate_overall_sentiment(news_sentiment, social_sentiment)
            
            # Generate sentiment trend
            sentiment_trend = await self._generate_sentiment_trend(symbol, timeframe)
            
            # Count total analyzed items
            sample_size = len(news_data) + len(social_data)
            
            return SentimentAnalysis(
                symbol=symbol,
                overall_sentiment=overall_sentiment,
                news_sentiment=news_sentiment,
                social_sentiment=social_sentiment,
                sentiment_trend=sentiment_trend,
                analyzed_at=datetime.utcnow(),
                sample_size=sample_size
            )
            
        except Exception as e:
            logger.error("Error analyzing sentiment", symbol=symbol, error=str(e))
            raise
    
    async def _fetch_news_data(self, symbol: str, timeframe: TimeFrame) -> List[NewsArticle]:
        """Fetch news data from various sources"""
        try:
            news_articles = []
            
            # Calculate date range based on timeframe
            end_date = datetime.utcnow()
            if timeframe == TimeFrame.ONE_DAY:
                start_date = end_date - timedelta(days=1)
            elif timeframe == TimeFrame.ONE_WEEK:
                start_date = end_date - timedelta(days=7)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Fetch from news sources
            if settings.NEWS_API_KEY:
                newsapi_articles = await self._fetch_from_newsapi(symbol, start_date, end_date)
                news_articles.extend(newsapi_articles)
            
            if settings.ALPHA_VANTAGE_API_KEY:
                av_articles = await self._fetch_from_alpha_vantage_news(symbol, start_date, end_date)
                news_articles.extend(av_articles)
            
            # Deduplicate articles
            unique_articles = self._deduplicate_articles(news_articles)
            
            logger.info("Fetched news articles", symbol=symbol, count=len(unique_articles))
            return unique_articles
            
        except Exception as e:
            logger.error("Error fetching news data", symbol=symbol, error=str(e))
            return []
    
    async def _fetch_social_data(self, symbol: str, timeframe: TimeFrame) -> List[SocialMediaPost]:
        """Fetch social media data"""
        try:
            social_posts = []
            
            # Calculate date range
            end_date = datetime.utcnow()
            if timeframe == TimeFrame.ONE_DAY:
                start_date = end_date - timedelta(days=1)
            elif timeframe == TimeFrame.ONE_WEEK:
                start_date = end_date - timedelta(days=7)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Fetch from social sources
            if settings.TWITTER_ENABLED and settings.TWITTER_BEARER_TOKEN:
                twitter_posts = await self._fetch_from_twitter(symbol, start_date, end_date)
                social_posts.extend(twitter_posts)
            
            if settings.REDDIT_ENABLED:
                reddit_posts = await self._fetch_from_reddit(symbol, start_date, end_date)
                social_posts.extend(reddit_posts)
            
            logger.info("Fetched social media posts", symbol=symbol, count=len(social_posts))
            return social_posts
            
        except Exception as e:
            logger.error("Error fetching social data", symbol=symbol, error=str(e))
            return []
    
    async def _analyze_news_sentiment(self, news_articles: List[NewsArticle]) -> SentimentScore:
        """Analyze sentiment of news articles"""
        try:
            if not news_articles:
                return None
            
            # Extract text content
            texts = []
            for article in news_articles:
                # Combine title and content
                text = f"{article.title}. {article.content[:500]}"
                texts.append(text)
            
            # Analyze sentiment using FinBERT
            sentiment_results = await self.finbert_model.predict_batch(texts)
            
            # Aggregate results
            positive_count = sum(1 for r in sentiment_results if r['label'] == 'positive')
            negative_count = sum(1 for r in sentiment_results if r['label'] == 'negative')
            neutral_count = sum(1 for r in sentiment_results if r['label'] == 'neutral')
            
            # Calculate weighted scores
            total_confidence = sum(r['score'] for r in sentiment_results)
            positive_score = sum(r['score'] for r in sentiment_results if r['label'] == 'positive')
            negative_score = sum(r['score'] for r in sentiment_results if r['label'] == 'negative')
            
            # Determine overall sentiment
            if positive_count > negative_count:
                overall_label = SentimentLabel.POSITIVE
                overall_score = positive_score / total_confidence if total_confidence > 0 else 0
            elif negative_count > positive_count:
                overall_label = SentimentLabel.NEGATIVE
                overall_score = negative_score / total_confidence if total_confidence > 0 else 0
            else:
                overall_label = SentimentLabel.NEUTRAL
                overall_score = 0.5
            
            # Calculate compound score
            compound_score = (positive_score - negative_score) / total_confidence if total_confidence > 0 else 0
            
            return SentimentScore(
                label=overall_label,
                score=overall_score,
                compound_score=compound_score
            )
            
        except Exception as e:
            logger.error("Error analyzing news sentiment", error=str(e))
            return None
    
    async def _analyze_social_sentiment(self, social_posts: List[SocialMediaPost]) -> SentimentScore:
        """Analyze sentiment of social media posts"""
        try:
            if not social_posts:
                return None
            
            # Extract text content
            texts = [post.content for post in social_posts]
            
            # Analyze sentiment using FinBERT
            sentiment_results = await self.finbert_model.predict_batch(texts)
            
            # Weight by engagement metrics
            weighted_results = []
            for i, result in enumerate(sentiment_results):
                post = social_posts[i]
                engagement = sum(post.engagement_metrics.values()) if post.engagement_metrics else 1
                weight = min(engagement, 100)  # Cap weight at 100
                
                weighted_results.append({
                    'label': result['label'],
                    'score': result['score'],
                    'weight': weight,
                    'compound_score': result['compound_score']
                })
            
            # Calculate weighted aggregation
            total_weight = sum(r['weight'] for r in weighted_results)
            if total_weight == 0:
                return None
            
            positive_weight = sum(r['weight'] for r in weighted_results if r['label'] == 'positive')
            negative_weight = sum(r['weight'] for r in weighted_results if r['label'] == 'negative')
            
            # Determine overall sentiment
            if positive_weight > negative_weight:
                overall_label = SentimentLabel.POSITIVE
                overall_score = positive_weight / total_weight
            elif negative_weight > positive_weight:
                overall_label = SentimentLabel.NEGATIVE
                overall_score = negative_weight / total_weight
            else:
                overall_label = SentimentLabel.NEUTRAL
                overall_score = 0.5
            
            # Calculate compound score
            weighted_compound = sum(r['compound_score'] * r['weight'] for r in weighted_results)
            compound_score = weighted_compound / total_weight
            
            return SentimentScore(
                label=overall_label,
                score=overall_score,
                compound_score=compound_score
            )
            
        except Exception as e:
            logger.error("Error analyzing social sentiment", error=str(e))
            return None
    
    async def _calculate_overall_sentiment(self, news_sentiment: SentimentScore, 
                                         social_sentiment: SentimentScore) -> SentimentScore:
        """Calculate overall sentiment from news and social sentiment"""
        try:
            # If only one source available, use it
            if news_sentiment and not social_sentiment:
                return news_sentiment
            elif social_sentiment and not news_sentiment:
                return social_sentiment
            elif not news_sentiment and not social_sentiment:
                # Return neutral sentiment
                return SentimentScore(
                    label=SentimentLabel.NEUTRAL,
                    score=0.5,
                    compound_score=0.0
                )
            
            # Weight news slightly higher than social media
            news_weight = 0.6
            social_weight = 0.4
            
            # Calculate weighted compound score
            weighted_compound = (news_sentiment.compound_score * news_weight + 
                               social_sentiment.compound_score * social_weight)
            
            # Determine overall label based on compound score
            if weighted_compound > 0.05:
                overall_label = SentimentLabel.POSITIVE
            elif weighted_compound < -0.05:
                overall_label = SentimentLabel.NEGATIVE
            else:
                overall_label = SentimentLabel.NEUTRAL
            
            # Calculate confidence score
            confidence_score = (news_sentiment.score * news_weight + 
                              social_sentiment.score * social_weight)
            
            return SentimentScore(
                label=overall_label,
                score=confidence_score,
                compound_score=weighted_compound
            )
            
        except Exception as e:
            logger.error("Error calculating overall sentiment", error=str(e))
            return SentimentScore(
                label=SentimentLabel.NEUTRAL,
                score=0.5,
                compound_score=0.0
            )
    
    # Placeholder methods for external data sources
    async def _fetch_from_newsapi(self, symbol: str, start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Fetch news from NewsAPI"""
        # Implementation would integrate with NewsAPI
        return []
    
    async def _fetch_from_alpha_vantage_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[NewsArticle]:
        """Fetch news from Alpha Vantage"""
        # Implementation would integrate with Alpha Vantage News API
        return []
    
    async def _fetch_from_twitter(self, symbol: str, start_date: datetime, end_date: datetime) -> List[SocialMediaPost]:
        """Fetch posts from Twitter"""
        # Implementation would integrate with Twitter API v2
        return []
    
    async def _fetch_from_reddit(self, symbol: str, start_date: datetime, end_date: datetime) -> List[SocialMediaPost]:
        """Fetch posts from Reddit"""
        # Implementation would integrate with Reddit API
        return []
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        # Simple deduplication based on title
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_key = article.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    async def _generate_sentiment_trend(self, symbol: str, timeframe: TimeFrame) -> List[Dict[str, Any]]:
        """Generate sentiment trend data"""
        # This would typically fetch historical sentiment data
        # For now, return empty list
        return []
    
    async def get_sentiment_trend(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get sentiment trend over specified number of days"""
        # Implementation would fetch historical sentiment data
        return []
    
    async def get_news_with_sentiment(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Get news articles with sentiment analysis"""
        try:
            news_articles = await self._fetch_news_data(symbol, TimeFrame.ONE_WEEK)
            
            # Limit results
            news_articles = news_articles[:limit]
            
            # Analyze sentiment for each article
            results = []
            for article in news_articles:
                text = f"{article.title}. {article.content[:500]}"
                sentiment = await self.finbert_model.predict_sentiment(text)
                
                results.append({
                    'title': article.title,
                    'content': article.content[:200] + "..." if len(article.content) > 200 else article.content,
                    'url': article.url,
                    'source': article.source,
                    'published_at': article.published_at,
                    'sentiment': sentiment
                })
            
            return results
            
        except Exception as e:
            logger.error("Error getting news with sentiment", symbol=symbol, error=str(e))
            return []
    
    async def get_social_media_sentiment(self, symbol: str, platform: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Get social media posts with sentiment analysis"""
        try:
            social_posts = await self._fetch_social_data(symbol, TimeFrame.ONE_WEEK)
            
            # Filter by platform if specified
            if platform:
                social_posts = [post for post in social_posts if post.platform.lower() == platform.lower()]
            
            # Limit results
            social_posts = social_posts[:limit]
            
            # Analyze sentiment for each post
            results = []
            for post in social_posts:
                sentiment = await self.finbert_model.predict_sentiment(post.content)
                
                results.append({
                    'platform': post.platform,
                    'content': post.content,
                    'author': post.author,
                    'posted_at': post.posted_at,
                    'engagement_metrics': post.engagement_metrics,
                    'sentiment': sentiment
                })
            
            return results
            
        except Exception as e:
            logger.error("Error getting social media sentiment", symbol=symbol, error=str(e))
            return []
    
    async def bulk_sentiment_analysis(self, symbols: List[str], timeframe: TimeFrame) -> List[SentimentAnalysis]:
        """Perform sentiment analysis for multiple symbols"""
        try:
            tasks = []
            for symbol in symbols:
                task = self.analyze_sentiment(symbol, timeframe)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error("Error in bulk sentiment analysis", symbol=symbols[i], error=str(result))
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error("Error in bulk sentiment analysis", symbols=symbols, error=str(e))
            return []
    
    async def get_market_sentiment_overview(self, sector: Optional[str] = None) -> Dict[str, Any]:
        """Get market-wide sentiment overview"""
        try:
            # This would typically aggregate sentiment across market sectors
            # For now, return a placeholder
            
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.5,
                'sector_breakdown': {},
                'trending_positive': [],
                'trending_negative': [],
                'updated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error getting market sentiment overview", error=str(e))
            return {}