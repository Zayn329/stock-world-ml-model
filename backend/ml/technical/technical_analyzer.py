import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Any, Optional, Tuple
import structlog
from datetime import datetime, timedelta
import yfinance as yf

logger = structlog.get_logger(__name__)


class TechnicalAnalyzer:
    """
    Technical analysis module for stock price analysis
    """
    
    def __init__(self):
        self.supported_indicators = [
            'SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ADX', 'CCI', 'ROC', 
            'Stochastic', 'Williams', 'OBV', 'VWAP', 'ATR', 'Aroon'
        ]
        
        self.supported_patterns = [
            'doji', 'hammer', 'hanging_man', 'shooting_star', 'engulfing',
            'harami', 'morning_star', 'evening_star', 'three_white_soldiers'
        ]
        
        self.timeframe_mapping = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1wk', '1M': '1mo'
        }
    
    async def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Ensure proper column names
            data.columns = [col.title() if col.lower() in ['open', 'high', 'low', 'close', 'volume'] else col for col in data.columns]
            
            return data
            
        except Exception as e:
            logger.error("Error fetching stock data", symbol=symbol, error=str(e))
            raise
    
    async def calculate_sma(self, data: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict[str, np.ndarray]:
        """Calculate Simple Moving Average"""
        sma_data = {}
        for period in periods:
            sma_data[f'SMA_{period}'] = talib.SMA(data['Close'].values, timeperiod=period)
        return sma_data
    
    async def calculate_ema(self, data: pd.DataFrame, periods: List[int] = [12, 26, 50]) -> Dict[str, np.ndarray]:
        """Calculate Exponential Moving Average"""
        ema_data = {}
        for period in periods:
            ema_data[f'EMA_{period}'] = talib.EMA(data['Close'].values, timeperiod=period)
        return ema_data
    
    async def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Relative Strength Index"""
        return talib.RSI(data['Close'].values, timeperiod=period)
    
    async def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, np.ndarray]:
        """Calculate MACD"""
        macd, macd_signal, macd_hist = talib.MACD(
            data['Close'].values, 
            fastperiod=fast, 
            slowperiod=slow, 
            signalperiod=signal
        )
        return {
            'MACD': macd,
            'MACD_Signal': macd_signal,
            'MACD_Histogram': macd_hist
        }
    
    async def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std: int = 2) -> Dict[str, np.ndarray]:
        """Calculate Bollinger Bands"""
        upper, middle, lower = talib.BBANDS(
            data['Close'].values, 
            timeperiod=period, 
            nbdevup=std, 
            nbdevdn=std
        )
        return {
            'BB_Upper': upper,
            'BB_Middle': middle,
            'BB_Lower': lower
        }
    
    async def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, np.ndarray]:
        """Calculate Stochastic Oscillator"""
        slowk, slowd = talib.STOCH(
            data['High'].values,
            data['Low'].values,
            data['Close'].values,
            fastk_period=k_period,
            slowk_period=d_period,
            slowd_period=d_period
        )
        return {
            'Stoch_K': slowk,
            'Stoch_D': slowd
        }
    
    async def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        return talib.ATR(data['High'].values, data['Low'].values, data['Close'].values, timeperiod=period)
    
    async def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate Average Directional Index"""
        return talib.ADX(data['High'].values, data['Low'].values, data['Close'].values, timeperiod=period)
    
    async def calculate_obv(self, data: pd.DataFrame) -> np.ndarray:
        """Calculate On-Balance Volume"""
        return talib.OBV(data['Close'].values, data['Volume'].values)
    
    async def calculate_vwap(self, data: pd.DataFrame) -> np.ndarray:
        """Calculate Volume Weighted Average Price"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        return (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    
    async def calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators"""
        indicators = {}
        
        try:
            # Moving Averages
            sma = await self.calculate_sma(data)
            ema = await self.calculate_ema(data)
            indicators.update(sma)
            indicators.update(ema)
            
            # Oscillators
            indicators['RSI'] = await self.calculate_rsi(data)
            macd = await self.calculate_macd(data)
            indicators.update(macd)
            
            stoch = await self.calculate_stochastic(data)
            indicators.update(stoch)
            
            # Volatility Indicators
            bb = await self.calculate_bollinger_bands(data)
            indicators.update(bb)
            indicators['ATR'] = await self.calculate_atr(data)
            
            # Trend Indicators
            indicators['ADX'] = await self.calculate_adx(data)
            
            # Volume Indicators
            indicators['OBV'] = await self.calculate_obv(data)
            indicators['VWAP'] = await self.calculate_vwap(data)
            
            return indicators
            
        except Exception as e:
            logger.error("Error calculating indicators", error=str(e))
            raise
    
    async def identify_support_resistance(self, data: pd.DataFrame, lookback: int = 50) -> Dict[str, List[float]]:
        """Identify support and resistance levels"""
        try:
            high_prices = data['High'].values
            low_prices = data['Low'].values
            
            # Find local peaks and troughs
            resistance_levels = []
            support_levels = []
            
            for i in range(lookback, len(high_prices) - lookback):
                # Check for resistance (local maxima)
                if all(high_prices[i] >= high_prices[i-j] for j in range(1, lookback+1)) and \
                   all(high_prices[i] >= high_prices[i+j] for j in range(1, lookback+1)):
                    resistance_levels.append(high_prices[i])
                
                # Check for support (local minima)
                if all(low_prices[i] <= low_prices[i-j] for j in range(1, lookback+1)) and \
                   all(low_prices[i] <= low_prices[i+j] for j in range(1, lookback+1)):
                    support_levels.append(low_prices[i])
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
            support_levels = sorted(list(set(support_levels)))[:5]
            
            return {
                'resistance_levels': resistance_levels,
                'support_levels': support_levels
            }
            
        except Exception as e:
            logger.error("Error identifying support/resistance", error=str(e))
            raise
    
    async def generate_trading_signals(self, data: pd.DataFrame, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals based on technical indicators"""
        signals = []
        current_price = data['Close'].iloc[-1]
        
        try:
            # RSI Signals
            rsi = indicators.get('RSI')
            if rsi is not None and not np.isnan(rsi[-1]):
                if rsi[-1] < 30:
                    signals.append({
                        'type': 'buy',
                        'indicator': 'RSI',
                        'value': rsi[-1],
                        'signal': 'oversold',
                        'strength': 'strong' if rsi[-1] < 20 else 'medium',
                        'timestamp': datetime.utcnow()
                    })
                elif rsi[-1] > 70:
                    signals.append({
                        'type': 'sell',
                        'indicator': 'RSI',
                        'value': rsi[-1],
                        'signal': 'overbought',
                        'strength': 'strong' if rsi[-1] > 80 else 'medium',
                        'timestamp': datetime.utcnow()
                    })
            
            # MACD Signals
            macd = indicators.get('MACD')
            macd_signal = indicators.get('MACD_Signal')
            if macd is not None and macd_signal is not None:
                if len(macd) > 1 and len(macd_signal) > 1:
                    if macd[-1] > macd_signal[-1] and macd[-2] <= macd_signal[-2]:
                        signals.append({
                            'type': 'buy',
                            'indicator': 'MACD',
                            'signal': 'bullish_crossover',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
                    elif macd[-1] < macd_signal[-1] and macd[-2] >= macd_signal[-2]:
                        signals.append({
                            'type': 'sell',
                            'indicator': 'MACD',
                            'signal': 'bearish_crossover',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
            
            # Moving Average Signals
            sma_20 = indicators.get('SMA_20')
            sma_50 = indicators.get('SMA_50')
            if sma_20 is not None and sma_50 is not None:
                if not np.isnan(sma_20[-1]) and not np.isnan(sma_50[-1]):
                    if current_price > sma_20[-1] > sma_50[-1]:
                        signals.append({
                            'type': 'buy',
                            'indicator': 'Moving Average',
                            'signal': 'bullish_alignment',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
                    elif current_price < sma_20[-1] < sma_50[-1]:
                        signals.append({
                            'type': 'sell',
                            'indicator': 'Moving Average',
                            'signal': 'bearish_alignment',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
            
            # Bollinger Bands Signals
            bb_upper = indicators.get('BB_Upper')
            bb_lower = indicators.get('BB_Lower')
            if bb_upper is not None and bb_lower is not None:
                if not np.isnan(bb_upper[-1]) and not np.isnan(bb_lower[-1]):
                    if current_price <= bb_lower[-1]:
                        signals.append({
                            'type': 'buy',
                            'indicator': 'Bollinger Bands',
                            'signal': 'oversold_bounce',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
                    elif current_price >= bb_upper[-1]:
                        signals.append({
                            'type': 'sell',
                            'indicator': 'Bollinger Bands',
                            'signal': 'overbought_rejection',
                            'strength': 'medium',
                            'timestamp': datetime.utcnow()
                        })
            
            return signals
            
        except Exception as e:
            logger.error("Error generating trading signals", error=str(e))
            return signals
    
    async def calculate_volatility(self, data: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """Calculate various volatility measures"""
        try:
            returns = data['Close'].pct_change().dropna()
            
            # Historical volatility (annualized)
            historical_vol = returns.rolling(window=period).std() * np.sqrt(252)
            
            # Average True Range percentage
            atr = await self.calculate_atr(data, period)
            atr_percentage = (atr / data['Close']) * 100
            
            # Bollinger Band width
            bb = await self.calculate_bollinger_bands(data, period)
            bb_width = ((bb['BB_Upper'] - bb['BB_Lower']) / bb['BB_Middle']) * 100
            
            return {
                'historical_volatility': float(historical_vol.iloc[-1]) if not np.isnan(historical_vol.iloc[-1]) else 0.0,
                'atr_percentage': float(atr_percentage[-1]) if not np.isnan(atr_percentage[-1]) else 0.0,
                'bollinger_width': float(bb_width[-1]) if not np.isnan(bb_width[-1]) else 0.0,
                'volatility_rank': self._calculate_volatility_rank(historical_vol.iloc[-1], historical_vol)
            }
            
        except Exception as e:
            logger.error("Error calculating volatility", error=str(e))
            return {}
    
    def _calculate_volatility_rank(self, current_vol: float, historical_vols: pd.Series) -> str:
        """Calculate volatility rank (low, medium, high)"""
        try:
            percentile = (historical_vols < current_vol).mean() * 100
            
            if percentile < 25:
                return "low"
            elif percentile < 75:
                return "medium"
            else:
                return "high"
        except:
            return "unknown"
    
    async def identify_trend_direction(self, data: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Identify overall trend direction"""
        try:
            trend_indicators = []
            
            # Moving averages trend
            sma_20 = indicators.get('SMA_20')
            sma_50 = indicators.get('SMA_50')
            sma_200 = indicators.get('SMA_200')
            
            current_price = data['Close'].iloc[-1]
            
            if all(x is not None for x in [sma_20, sma_50, sma_200]):
                if (current_price > sma_20[-1] > sma_50[-1] > sma_200[-1]):
                    trend_indicators.append("bullish")
                elif (current_price < sma_20[-1] < sma_50[-1] < sma_200[-1]):
                    trend_indicators.append("bearish")
                else:
                    trend_indicators.append("sideways")
            
            # ADX trend strength
            adx = indicators.get('ADX')
            if adx is not None and not np.isnan(adx[-1]):
                if adx[-1] > 25:
                    trend_indicators.append("strong_trend")
                else:
                    trend_indicators.append("weak_trend")
            
            # Determine overall trend
            if trend_indicators.count("bullish") > trend_indicators.count("bearish"):
                overall_trend = "bullish"
            elif trend_indicators.count("bearish") > trend_indicators.count("bullish"):
                overall_trend = "bearish"
            else:
                overall_trend = "sideways"
            
            return {
                'direction': overall_trend,
                'strength': 'strong' if 'strong_trend' in trend_indicators else 'weak',
                'confidence': len([x for x in trend_indicators if x in ['bullish', 'bearish']]) / len(trend_indicators),
                'supporting_indicators': trend_indicators
            }
            
        except Exception as e:
            logger.error("Error identifying trend direction", error=str(e))
            return {'direction': 'unknown', 'strength': 'unknown', 'confidence': 0.0}