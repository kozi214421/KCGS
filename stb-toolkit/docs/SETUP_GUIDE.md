# STB Toolkit Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [TradingView Setup](#tradingview-setup)
3. [Indicator Installation](#indicator-installation)
4. [Strategy Configuration](#strategy-configuration)
5. [Webhook Setup](#webhook-setup)
6. [Data Source Configuration](#data-source-configuration)
7. [Testing and Validation](#testing-and-validation)

## Prerequisites

### Required Accounts
- **TradingView**: Premium account (for alerts and strategy testing)
- **Data Providers** (Optional for enrichment):
  - FINRA API account (short interest data)
  - Unusual Whales subscription (options flow)
  - Quiver Quant API access (dark pool data)

### Technical Requirements
- Python 3.8 or higher (for webhook handler)
- Web server or cloud platform (for webhook hosting)
- Basic understanding of Pine Script and trading concepts

## TradingView Setup

### 1. Access Pine Editor
1. Log into TradingView
2. Navigate to the Chart view
3. Click on "Pine Editor" at the bottom of the screen

### 2. Verify Account Level
- Ensure you have a Premium, Pro, or Pro+ account for:
  - Multiple alerts
  - Strategy backtesting
  - Webhook functionality

## Indicator Installation

### Step 1: Load the STB Indicator

1. Open the Pine Editor in TradingView
2. Copy the entire contents of `indicators/stb_20_signal_breakout.pine`
3. Paste into the Pine Editor
4. Click "Add to Chart"

### Step 2: Configure Indicator Settings

#### Technical Indicators
```
RSI Period: 14 (default)
RSI Overbought: 70
RSI Oversold: 30
MACD Fast: 12
MACD Slow: 26
MACD Signal: 9
Bollinger Bands Length: 20
Bollinger Bands Multiplier: 2.0
```

#### Moving Averages
```
SMA Short Period: 20
SMA Medium Period: 50
SMA Long Period: 200
EMA Period: 21
```

#### Volume Analysis
```
Volume MA Period: 20
Volume Spike Multiplier: 2.0
```

#### VWAP Settings
```
VWAP Period: D (Daily)
VWAP Bands Multiplier: 1.0
```

#### Relative Strength
```
RS Compare Symbol: SPY (or any benchmark)
```

#### Signal Threshold
```
Signal Threshold: 12 (minimum signals required for alert)
Adjust between 10-16 based on risk tolerance:
- 10-12: More signals, higher false positives
- 13-15: Balanced approach
- 16-20: Fewer signals, higher confidence
```

### Step 3: Visual Customization

1. Right-click on the indicator name
2. Select "Settings"
3. Navigate to "Style" tab
4. Customize colors and line widths as desired

## Strategy Configuration

### For Backtesting (Optional)

1. Open Pine Editor
2. Copy contents of `strategies/stb_20_signal_strategy.pine`
3. Paste into Pine Editor
4. Click "Add to Chart"

### Strategy Parameters

#### Risk Management
```
Use Stop Loss: true
Stop Loss %: 2.0
Use Take Profit: true
Take Profit %: 4.0
Use Trailing Stop: false
Trailing Stop %: 1.5
```

#### Position Sizing
```
Risk Per Trade %: 2.0 (of total equity)
```

#### Signal Thresholds
```
Signal Threshold: 12 (entry)
Exit Signal Threshold: 10 (exit)
```

### Backtesting Steps

1. Add strategy to chart
2. Open "Strategy Tester" tab (bottom panel)
3. Review performance metrics:
   - Net Profit
   - Profit Factor
   - Max Drawdown
   - Win Rate
   - Sharpe Ratio
4. Adjust parameters for optimization
5. Use "Deep Backtesting" for more accurate results

## Webhook Setup

### Step 1: Deploy Webhook Handler

#### Option A: Local Development
```bash
# Install dependencies
pip install flask requests

# Set environment variables
export FINRA_API_KEY="your_key"
export UNUSUAL_WHALES_API_KEY="your_key"
export QUIVER_API_KEY="your_key"

# Run the server
python webhook_handler.py
```

#### Option B: Cloud Deployment (Heroku)
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create new app
heroku create stb-webhook-handler

# Set config vars
heroku config:set FINRA_API_KEY=your_key
heroku config:set UNUSUAL_WHALES_API_KEY=your_key
heroku config:set QUIVER_API_KEY=your_key

# Deploy
git push heroku main
```

#### Option C: Cloud Deployment (AWS Lambda)
1. Package webhook_handler.py with dependencies
2. Create Lambda function
3. Add API Gateway trigger
4. Configure environment variables
5. Set timeout to 30 seconds

### Step 2: Configure Webhook URL

1. Edit `webhooks/webhook_config.json`
2. Update the primary webhook URL:
```json
{
  "webhook_endpoints": {
    "primary": {
      "url": "https://your-server.com/api/stb-alerts",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Step 3: Create TradingView Alerts

1. Right-click on chart with STB indicator
2. Select "Add Alert"
3. Configure alert:
   - **Condition**: STB 20-Signal Breakout → STB Buy Signal (or Sell Signal)
   - **Options**: Once Per Bar Close
   - **Alert Actions**: Webhook URL
   - **Webhook URL**: Your deployed webhook endpoint
   - **Message**: Use the built-in JSON message from indicator

Example alert message:
```json
{
  "signal": "BUY",
  "ticker": "{{ticker}}",
  "price": "{{close}}",
  "signals": "15",
  "time": "{{time}}"
}
```

### Step 4: Test Webhook

1. Trigger a test alert on TradingView
2. Check webhook logs for received data
3. Verify enrichment data is being fetched
4. Confirm notifications are being sent

## Data Source Configuration

### Short Interest (FINRA)

1. Register at https://www.finra.org/
2. Apply for API access
3. Obtain API key
4. Set environment variable: `FINRA_API_KEY`

### Options Flow (Unusual Whales)

1. Subscribe at https://unusualwhales.com/
2. Navigate to API section
3. Generate API key
4. Set environment variable: `UNUSUAL_WHALES_API_KEY`

### Dark Pool Data (Quiver Quant)

1. Sign up at https://www.quiverquant.com/
2. Subscribe to dark pool data feed
3. Generate API key
4. Set environment variable: `QUIVER_API_KEY`

### Institutional Data (SEC EDGAR)

- No API key required
- Public data from SEC filings
- Automatically fetched when enabled

## Testing and Validation

### Indicator Validation

1. **Signal Accuracy**
   - Compare signals against manual analysis
   - Verify signal counts match criteria
   - Check for false positives

2. **Performance Testing**
   - Load indicator on various timeframes
   - Test with different symbols
   - Verify calculation speed

### Strategy Validation

1. **Backtest Results**
   - Run 1-year backtest minimum
   - Compare to buy-and-hold
   - Analyze drawdown periods
   - Review trade distribution

2. **Forward Testing**
   - Paper trade for 1-2 months
   - Track signal performance
   - Compare to backtest results

### Webhook Validation

1. **Connection Test**
```bash
curl -X POST https://your-server.com/health
```

2. **Alert Test**
```bash
curl -X POST https://your-server.com/api/stb-alerts \
  -H "Content-Type: application/json" \
  -d '{"signal":"BUY","ticker":"AAPL","price":"150.00","signals":"15","time":"2024-01-01 10:00:00"}'
```

3. **Enrichment Verification**
   - Check logs for API calls
   - Verify data is being cached
   - Confirm all enrichment sources are working

### Monitoring

1. **Daily Checks**
   - Verify alerts are being triggered
   - Check webhook logs for errors
   - Monitor API rate limits

2. **Weekly Reviews**
   - Analyze signal performance
   - Review enriched data quality
   - Adjust parameters if needed

## Troubleshooting

### Common Issues

1. **No Alerts Triggering**
   - Verify signal threshold isn't too high
   - Check alert is set to "Once Per Bar Close"
   - Ensure Premium account is active

2. **Webhook Not Receiving Data**
   - Verify URL is publicly accessible
   - Check firewall settings
   - Test with curl command

3. **Enrichment Data Missing**
   - Verify API keys are set correctly
   - Check API rate limits
   - Review error logs

4. **Strategy Not Executing**
   - Ensure sufficient capital
   - Check position sizing settings
   - Verify order settings in Strategy Properties

## Next Steps

- Review [ALERT_RULES.md](ALERT_RULES.md) for alert configuration
- Read [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md) for trading guidelines
- Check [DATA_SOURCES.md](DATA_SOURCES.md) for data provider details
- See [VALIDATION.md](VALIDATION.md) for system validation procedures
