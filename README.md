# 🚀 Crypto Alert Dashboard v2.0

cryptocurrency monitoring and alert system built with Streamlit, featuring real-time price tracking, intelligent alerts, database persistence, and comprehensive notification systems.

live link: https://crypto-manager.streamlit.app/

## Features

### Core Functionality
- **Real-time Price Tracking**: Live crypto prices from CoinGecko API
- **Smart Watchlist Management**: Add/remove coins with custom thresholds
- **Intelligent Alerts**: Above/below threshold alerts with notification system
- **Price History Analysis**: Interactive charts with multiple timeframes
- **Data Export**: CSV downloads for price history and alerts




### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd crypto_alert
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate     # macOS/Linux
   # or
   venv\Scripts\activate        # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual values
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Environment Variables

Copy `env_template.txt` to `.env` and configure:

```bash
# API Keys
GNEWS_API_KEY=your_gnews_api_key_here

# Email Notifications
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_SERVER=smtp.gmail.com
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com

# Webhook Notifications
WEBHOOK_NOTIFICATIONS_ENABLED=false
WEBHOOK_URL=https://your-webhook-url.com/webhook

# Database
DB_HOST=localhost
DB_NAME=crypto_alert
DB_USER=your_username
DB_PASSWORD=your_password
```

### Configuration File

The `config.yaml` file contains application settings:

```yaml
app:
  name: "Crypto Alert Dashboard"
  version: "2.0.0"
  auto_refresh_interval: 60000

api:
  coingecko:
    base_url: "https://api.coingecko.com/api/v3"
    timeout: 10
    rate_limit_delay: 1.1
```

## Usage

### Dashboard Tab
- **Current Prices**: Real-time price display with alert status
- **Market Summary**: Overview of tracked coins and market data
- **Auto-refresh**: Configurable automatic data updates

### Watchlist Tab
- **Add Coins**: Add new cryptocurrencies with custom thresholds
- **Manage Alerts**: Set above/below price alerts
- **Remove Coins**: Remove coins from tracking

### Price History Tab
- **Interactive Charts**: Plotly-powered price visualizations
- **Multiple Timeframes**: 1d, 7d, 30d, 90d views
- **Data Export**: Download price history as CSV

### Alerts Tab
- **Alert History**: View and manage triggered alerts
- **Notification Settings**: Configure email and webhook alerts
- **Alert Management**: Acknowledge and track alerts

### Settings Tab
- **Configuration**: View and reload application settings
- **Database Management**: Stats, backup, and optimization
- **System Information**: Version and status details

## Development

### Code Structure
- **Modular Design**: Separate modules for different functionality
- **Type Hints**: Full type annotation support
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging throughout the application

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=.
```


## 🚨 Alert System

### Alert Types
- **Above Threshold**: Triggered when price exceeds upper limit
- **Below Threshold**: Triggered when price falls below lower limit
- **Percentage Change**: Future feature for percentage-based alerts
- **Volatility**: Future feature for volatility-based alerts

### Notification Channels
- **Email**: SMTP-based email notifications
- **Webhook**: HTTP POST to custom endpoints
- **SMS**: Twilio integration (optional)

### Alert Management
- **History Tracking**: Complete alert history in database
- **Acknowledgment**: Mark alerts as acknowledged
- **Rate Limiting**: Prevent notification spam
- **Custom Messages**: Personalized alert messages

## 📊 Database

### Tables
- **watchlist**: Coin tracking and threshold settings
- **price_history**: Historical price data with metadata
- **alerts**: Alert history and status
- **notifications**: Notification delivery tracking
- **user_preferences**: User settings and preferences

### Features
- **Automatic Backups**: Scheduled database backups
- **Data Cleanup**: Automatic cleanup of old records
- **Performance Indexes**: Optimized database queries
- **Connection Pooling**: Efficient database connections

## 🔒 Security

### Features
- **Environment Variables**: Secure credential management
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API abuse prevention
- **Error Handling**: Secure error messages

### Best Practices
- **Never commit .env files**: Use environment variables
- **Regular updates**: Keep dependencies updated
- **Access control**: Limit database access
- **Monitoring**: Monitor for suspicious activity

## 🚀 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit Cloud dashboard
4. Deploy automatically

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Environment Variables
Set these in your deployment environment:
- `GNEWS_API_KEY`
- `EMAIL_NOTIFICATIONS_ENABLED`
- `SMTP_SERVER`
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`


### Common Issues
1. **API Rate Limits**: CoinGecko has rate limits; increase delays if needed
2. **Database Errors**: Check file permissions and disk space
3. **Email Issues**: Verify SMTP settings and app passwords
4. **Import Errors**: Ensure all dependencies are installed

Author:
Haris Kamran
=======