import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manages multiple data sources for price data"""
    
    def __init__(self):
        self.alpha_vantage = AlphaVantageSource()
        self.manual_data = ManualDataSource()
        
    def get_price_data(self, symbol, timeframe='1h', limit=100):
        """Try multiple data sources in order of preference"""
        try:
            # Try Alpha Vantage first
            data = self.alpha_vantage.get_data(symbol, timeframe, limit)
            if data is not None and not data.empty:
                return data
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
        
        try:
            # Fallback to manual data
            data = self.manual_data.get_data(symbol, timeframe, limit)
            if data is not None and not data.empty:
                return data
        except Exception as e:
            logger.warning(f"Manual data failed for {symbol}: {e}")
        
        return None


class AlphaVantageSource:
    """Alpha Vantage API data source"""
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        
    def get_data(self, symbol, timeframe='1h', limit=100):
        """Fetch data from Alpha Vantage"""
        try:
            if timeframe == '1h':
                data, meta_data = self.ts.get_intraday(
                    symbol=symbol, 
                    interval='60min', 
                    outputsize='compact'
                )
            elif timeframe == '1d':
                data, meta_data = self.ts.get_daily(symbol=symbol, outputsize='compact')
            else:
                return None
                
            if data.empty:
                return None
                
            # Rename columns to standard format
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            data.index.name = 'timestamp'
            
            # Sort by timestamp and limit results
            data = data.sort_index(ascending=False).head(limit)
            
            return data
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None


class ManualDataSource:
    """Manual data input source for testing"""
    
    def __init__(self):
        self.mock_data = {}
        
    def add_manual_data(self, symbol, price_data):
        """Add manual price data for testing"""
        self.mock_data[symbol] = price_data
        
    def get_data(self, symbol, timeframe='1h', limit=100):
        """Get manual data if available"""
        if symbol in self.mock_data:
            return self.mock_data[symbol].head(limit)
        
        # Generate mock data for demo purposes
        return self._generate_mock_data(symbol, limit)
    
    def _generate_mock_data(self, symbol, limit):
        """Generate realistic mock data for demo"""
        try:
            # Base price varies by symbol - OTC pairs from Quotex
            base_prices = {
                # Popular OTC pairs
                'EURUSD_OTC': 1.0850,
                'GBPUSD_OTC': 1.2650,
                'USDJPY_OTC': 149.50,
                'AUDUSD_OTC': 0.6750,
                
                # Quotex OTC Currency pairs (from image)
                'NZDJPY_OTC': 89.45,
                'AUDCAD_OTC': 0.9125,
                'EURCAD_OTC': 1.4680,
                'USDBRL_OTC': 5.1250,
                'NZDCAD_OTC': 0.8340,
                'USDPHP_OTC': 56.75,
                'USDCOP_OTC': 4125.50,
                'USDIDR_OTC': 15650.00,
                'EURGBP_OTC': 0.8580,
                'GBPCHF_OTC': 1.1125,
                'GBPNZD_OTC': 2.0450,
                
                # Additional OTC pairs
                'USDCAD_OTC': 1.3550,
                'USDCHF_OTC': 0.8750,
                'EURJPY_OTC': 162.25,
                'GBPJPY_OTC': 189.75,
                'AUDNZD_OTC': 1.0850,
                
                # Fallback for any other symbols
                'DEFAULT': 1.0000,
            }
            
            base_price = base_prices.get(symbol, base_prices['DEFAULT'])
            
            # Generate timestamps
            end_time = datetime.now()
            timestamps = [end_time - timedelta(hours=i) for i in range(limit)]
            timestamps.reverse()
            
            # Generate realistic price movements with trends
            np.random.seed(hash(symbol) % 1000)  # Different seed per symbol
            
            # Create trending behavior for better technical analysis
            trend_strength = np.random.choice([-0.0005, 0, 0.0005], p=[0.3, 0.4, 0.3])
            returns = np.random.normal(trend_strength, 0.002, limit)  # Slightly larger movements with trend
            
            prices = [base_price]
            for i in range(1, limit):
                new_price = prices[-1] * (1 + returns[i])
                prices.append(new_price)
            
            # Create OHLCV data
            data = []
            for i, (timestamp, close) in enumerate(zip(timestamps, prices)):
                high = close * (1 + abs(np.random.normal(0, 0.0005)))
                low = close * (1 - abs(np.random.normal(0, 0.0005)))
                open_price = prices[i-1] if i > 0 else close
                volume = np.random.randint(1000, 10000)
                
                data.append({
                    'timestamp': timestamp,
                    'open': open_price,
                    'high': max(open_price, high, close),
                    'low': min(open_price, low, close),
                    'close': close,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Mock data generation error for {symbol}: {e}")
            return None


class WebScrapingSource:
    """Web scraping source (placeholder for future implementation)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_data(self, symbol, timeframe='1h', limit=100):
        """Placeholder for web scraping implementation"""
        # This would implement actual web scraping logic
        # For now, return None to fall back to other sources
        return None