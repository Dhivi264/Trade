# Quotex Trading Predictor

A sophisticated web-based trading tool that provides AI-powered price direction predictions for the Quotex platform with a focus on maintaining 90%+ accuracy threshold.

## Features

### Core Functionality
- **Real-time Price Predictions**: Generate directional forecasts (UP/DOWN) for 1-minute and 5-minute timeframes
- **90% Accuracy Threshold**: Only displays predictions that meet or exceed 90% confidence levels
- **Multiple Data Sources**: Supports Alpha Vantage API, manual price input, and extensible for web scraping
- **Technical Analysis**: Advanced indicators including RSI, MACD, Moving Averages, Bollinger Bands, Stochastic, Williams %R
- **Real-time Updates**: Automatic price and prediction updates
- **Historical Tracking**: Comprehensive accuracy metrics and prediction history

### Trading Pairs Supported
- EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD
- BTC/USD, ETH/USD
- XAU/USD (Gold)

### User Interface
- **Responsive Design**: Optimized for both mobile and desktop
- **Real-time Dashboard**: Live predictions, accuracy metrics, and price updates
- **Color-coded Predictions**: Green for UP, Red for DOWN predictions
- **Performance Metrics**: Win/loss ratios, accuracy percentages, session statistics
- **Clean Interface**: Fast-loading, intuitive design for quick decision-making

## Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for advanced frontend features)
- Redis (for background tasks)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd quotex-predictor
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp quotex_predictor/.env.example quotex_predictor/.env
# Edit .env file with your API keys and settings
```

5. **Database setup**
```bash
cd quotex_predictor
python manage.py makemigrations
python manage.py migrate
python manage.py setup_trading_pairs
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Configuration

### Alpha Vantage API
1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Add your API key to the `.env` file:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### Redis Setup (Optional)
For production environments with background tasks:
```bash
# Install Redis
# Windows: Download from https://redis.io/download
# Ubuntu: sudo apt-get install redis-server
# Mac: brew install redis

# Start Redis server
redis-server
```

## Usage

### Basic Operation
1. **Select Trading Pair**: Choose from the dropdown menu
2. **Choose Timeframe**: Select 1-minute or 5-minute prediction window
3. **Generate Prediction**: Click the prediction button
4. **View Results**: Only predictions meeting 90%+ confidence threshold are displayed

### API Endpoints
- `GET /api/trading-pairs/` - List available trading pairs
- `POST /api/prediction/` - Generate new prediction
- `GET /api/accuracy/` - Get accuracy metrics
- `GET /api/recent-predictions/` - Fetch recent predictions
- `GET /api/current-price/` - Get current price for symbol
- `POST /api/manual-price/` - Add manual price data (testing)

### Manual Price Input (Testing)
For testing without API access:
```bash
curl -X POST http://localhost:8000/api/manual-price/ \
  -H "Content-Type: application/json" \
  -d '{"symbol": "EURUSD", "price": 1.0850}'
```

## Technical Analysis Details

### Indicators Used
- **RSI (14)**: Relative Strength Index for momentum
- **MACD**: Moving Average Convergence Divergence
- **SMA/EMA**: Simple and Exponential Moving Averages (20, 50)
- **Bollinger Bands**: Volatility and mean reversion
- **Stochastic Oscillator**: Momentum indicator
- **Williams %R**: Momentum indicator
- **ATR**: Average True Range for volatility
- **Volume Analysis**: Volume-based confirmations

### Prediction Algorithm
The system uses a weighted scoring approach:
1. Each indicator generates a directional signal (UP/DOWN)
2. Signals are weighted based on reliability and market conditions
3. Confidence is calculated using signal consensus and volatility
4. Only predictions exceeding 90% confidence threshold are displayed
5. Historical accuracy is tracked and used for model validation

## Data Sources

### Primary: Alpha Vantage API
- Real-time and historical price data
- Multiple timeframes supported
- Rate limits: 5 calls per minute (free tier)

### Fallback: Manual Input
- Manual price entry for testing
- Mock data generation for demonstrations
- Useful when API limits are reached

### Future: Web Scraping (Extensible)
- Framework ready for web scraping implementation
- Can be extended to scrape financial websites
- Requires careful implementation to respect robots.txt

## Accuracy & Performance

### 90% Threshold System
- Predictions below 90% confidence are filtered out
- Maintains high reliability for trading decisions
- Reduces false signals and improves decision quality

### Performance Tracking
- Real-time accuracy calculation
- Historical win/loss ratios
- Per-symbol and per-timeframe metrics
- Continuous model validation

### Optimization Features
- Automatic reconnection on data source failures
- Efficient caching for repeated requests
- Responsive design for mobile trading
- Real-time updates without page refresh

## Production Deployment

### Environment Variables
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
ALPHA_VANTAGE_API_KEY=your_api_key
REDIS_URL=redis://localhost:6379/0
```

### Database
For production, consider PostgreSQL:
```bash
pip install psycopg2-binary
# Update DATABASE_URL in .env
```

### Web Server
Use Gunicorn + Nginx for production:
```bash
pip install gunicorn
gunicorn quotex_predictor.wsgi:application
```

## Troubleshooting

### Common Issues
1. **API Rate Limits**: Alpha Vantage free tier has 5 calls/minute limit
2. **No Predictions**: Check if confidence threshold is being met
3. **Data Source Errors**: Verify API keys and network connectivity
4. **Redis Connection**: Ensure Redis server is running for background tasks

### Debug Mode
Enable detailed logging in settings.py:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'predictor': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Trading involves significant risk, and past performance does not guarantee future results. Always conduct your own research and consider consulting with financial advisors before making trading decisions.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This tool provides predictions based on technical analysis and should be used as part of a comprehensive trading strategy. The 90% accuracy threshold is a confidence measure, not a guarantee of trading success.