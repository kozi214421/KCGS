# STB Toolkit Alert Rules and Configuration

## Overview

The STB Toolkit uses a sophisticated 20-signal system to generate trading alerts. This document explains how to configure and optimize alert rules for different trading styles and market conditions.

## Signal Categories

### 1. Technical Indicators (4 signals)
- **RSI Oversold/Overbought**: Traditional momentum reversal signals
- **MACD Crossover**: Trend change detection
- **MACD Momentum**: Histogram acceleration/deceleration
- **Bollinger Bands**: Price extremes and mean reversion

### 2. Moving Average Signals (5 signals)
- **SMA 20 Trend**: Short-term trend direction
- **SMA 50 Trend**: Medium-term trend direction
- **SMA 200 Position**: Long-term trend bias
- **Golden/Death Cross**: Major trend reversals
- **Price Cross SMA 20**: Immediate entry trigger

### 3. Volume Analysis (3 signals)
- **Volume Spike**: Unusual activity detection
- **Volume Trend**: Confirmation of price movement
- **Volume Increasing**: Momentum building

### 4. VWAP/AVWAP (3 signals)
- **VWAP Crossover**: Institutional support/resistance
- **VWAP Position**: Above/below fair value
- **VWAP Bands**: Extreme price deviation

### 5. Relative Strength (1 signal)
- **RS vs Benchmark**: Outperformance detection

### 6. Momentum Indicators (2 signals)
- **Stochastic**: Oversold/overbought conditions
- **ADX with DI**: Trend strength confirmation

### 7. Price Action (2 signals)
- **Breakout/Breakdown**: Prior high/low breach
- **EMA 21 Trend**: Dynamic support/resistance

## Alert Configuration

### Signal Threshold Settings

#### Conservative (16-18 signals)
```pine
signal_threshold = 16
```
- **Use Case**: Low-risk, high-confidence trades
- **Expected Frequency**: 2-5 signals per month per symbol
- **Win Rate**: 65-75%
- **Best For**: Swing trading, position trading

#### Balanced (12-15 signals)
```pine
signal_threshold = 12  // Default
```
- **Use Case**: Standard risk-reward balance
- **Expected Frequency**: 10-20 signals per month per symbol
- **Win Rate**: 55-65%
- **Best For**: Day trading, swing trading

#### Aggressive (10-11 signals)
```pine
signal_threshold = 10
```
- **Use Case**: Active trading, more opportunities
- **Expected Frequency**: 30-50 signals per month per symbol
- **Win Rate**: 45-55%
- **Best For**: Scalping, day trading

### Alert Types

#### 1. Standard Buy/Sell Signals
```
Condition: Bullish/Bearish signals >= threshold
Frequency: Once Per Bar Close
Expiration: Open-ended
```

**TradingView Alert Settings:**
```
Condition: STB 20-Signal Breakout
Alert name: STB Buy Signal - {{ticker}}
Message: {"signal":"BUY","ticker":"{{ticker}}","price":"{{close}}","signals":"15","time":"{{time}}"}
```

#### 2. Strong Breakout Alerts
```
Condition: Bullish signals >= 16
Frequency: Once Per Bar Close
Expiration: Open-ended
```

**Use Case**: High-confidence setups requiring immediate attention

#### 3. Multi-Timeframe Alerts

**Setup Example:**
1. Daily chart: signal_threshold = 12
2. 4-hour chart: signal_threshold = 13
3. 1-hour chart: signal_threshold = 14

**Alert Strategy:**
- Primary: Daily signals for position entries
- Secondary: 4-hour for timing optimization
- Tertiary: 1-hour for precision entries

### Watchlist Organization

#### Tier 1: High Priority
- Large-cap stocks (>$10B market cap)
- High liquidity (>5M daily volume)
- Threshold: 14+ signals

#### Tier 2: Medium Priority
- Mid-cap stocks ($2B-$10B)
- Moderate liquidity (1M-5M daily volume)
- Threshold: 12-13 signals

#### Tier 3: Speculative
- Small-cap stocks (<$2B)
- Lower liquidity (<1M daily volume)
- Threshold: 16+ signals (higher confidence required)

## Alert Filtering

### Pre-Alert Filters (Built into Indicator)

#### Volume Filter
```pine
volume_spike = volume > (volume_ma * 2.0)
```
- Ensures sufficient liquidity
- Reduces low-volume false signals

#### Trend Filter
```pine
ma_long_bull = close > sma_200
```
- Optional: Only trade with long-term trend
- Improves win rate in trending markets

### Post-Alert Filters (Webhook Level)

#### Price Range Filter
```json
"price_min": 1.0,
"price_max": null
```
- Exclude penny stocks
- Focus on tradeable securities

#### Market Cap Filter
```json
"market_cap_min": 100000000
```
- Minimum $100M market cap
- Reduces manipulation risk

#### Sector/Industry Filters
```json
"excluded_sectors": ["Utilities", "Real Estate"],
"excluded_tickers": ["XYZ", "ABC"]
```
- Customize based on strategy
- Avoid known problematic symbols

## Alert Timing

### Timeframe Selection

#### Daily Chart
- **Best For**: Swing trades (2-7 days)
- **Signal Quality**: Highest
- **Frequency**: Lowest
- **Recommended Threshold**: 12-14

#### 4-Hour Chart
- **Best For**: Short swing trades (1-3 days)
- **Signal Quality**: High
- **Frequency**: Medium
- **Recommended Threshold**: 13-15

#### 1-Hour Chart
- **Best For**: Day trades (same day exit)
- **Signal Quality**: Medium
- **Frequency**: High
- **Recommended Threshold**: 14-16

#### 15-Minute Chart
- **Best For**: Scalping (minutes to hours)
- **Signal Quality**: Lower
- **Frequency**: Very high
- **Recommended Threshold**: 16-18

### Market Session Timing

#### Pre-Market (4:00 AM - 9:30 AM ET)
- Lower liquidity
- Higher spreads
- Recommended: Disable alerts or increase threshold

#### Regular Hours (9:30 AM - 4:00 PM ET)
- Normal operations
- Standard thresholds

#### After-Hours (4:00 PM - 8:00 PM ET)
- Moderate liquidity
- Consider increasing threshold by 1-2 signals

## Alert Management

### Daily Routine

**Morning (Pre-Market):**
1. Review overnight alerts
2. Check enriched data for key signals
3. Prioritize high-signal-count alerts (15+)
4. Prepare watchlist for market open

**During Market:**
1. Monitor real-time alerts
2. Validate with chart analysis
3. Execute trades per risk management rules
4. Track entry prices and signals

**After-Hours:**
1. Review day's signals and performance
2. Adjust watchlist for next session
3. Check webhook logs for issues
4. Update alert thresholds if needed

### Alert Prioritization

#### Priority 1: Immediate Action
- 18+ signals
- High volume confirmation
- Strong institutional data (short squeeze, unusual options)

#### Priority 2: Review Within Hour
- 15-17 signals
- Normal volume
- Neutral institutional data

#### Priority 3: Monitor
- 12-14 signals
- Low volume warning
- No institutional confirmation

### False Positive Management

#### Common False Positive Scenarios
1. **Gap Events**: Price gaps can trigger multiple signals
   - Solution: Wait for gap fill or confirmation
   
2. **Earnings Reports**: Extreme volatility skews indicators
   - Solution: Disable alerts 1 day before/after earnings
   
3. **Low Liquidity**: Wide spreads cause signal distortion
   - Solution: Minimum volume filter (1M+ daily)

4. **Market Regime Changes**: Trending vs ranging markets
   - Solution: Adjust threshold seasonally

## Advanced Alert Strategies

### Multi-Symbol Correlation Alerts

**Setup:**
1. Create alerts for correlated symbols (e.g., tech stocks)
2. Require 2-3 symbols triggering simultaneously
3. Increases confidence in sector-wide moves

### Divergence Alerts

**Configuration:**
- Monitor when price makes new highs but signals decrease
- Indicates weakening momentum
- Use as exit signal for existing positions

### Volume-Weighted Alerts

**Enhancement:**
```pine
// Custom modification: Increase weight of volume signals
if (volume_spike and close > open) {
    bullish_signals := bullish_signals + 1  // Extra weight
}
```

### Institutional Confirmation Alerts

**Webhook Logic:**
```python
# Only forward alerts with institutional confirmation
if enriched_alert['institutional_data']['short_interest']['percent'] > 20:
    priority = "HIGH"  # Short squeeze potential
```

## Alert Optimization

### Backtesting Alert Rules

1. **Historical Analysis**
   - Review past signals at different thresholds
   - Calculate win rate per threshold level
   - Determine optimal threshold for your trading style

2. **Forward Testing**
   - Paper trade with current settings for 1 month
   - Track all signals and outcomes
   - Adjust based on real-world performance

3. **Ongoing Optimization**
   - Monthly review of alert performance
   - Seasonal adjustments (e.g., lower threshold in trends)
   - Market condition adaptations (bull vs bear markets)

### Performance Metrics

Track these metrics for each alert configuration:

```
Total Alerts: [count]
Signals Acted On: [count]
Win Rate: [percentage]
Average Gain: [percentage]
Average Loss: [percentage]
Profit Factor: [ratio]
False Positive Rate: [percentage]
```

## Notification Preferences

### Critical Alerts (16+ signals)
- **Discord**: Immediate ping with @role mention
- **Slack**: Urgent channel notification
- **Telegram**: Push notification
- **Email**: High-priority flag

### Standard Alerts (12-15 signals)
- **Discord**: Standard message
- **Slack**: Regular channel post
- **Telegram**: Silent notification
- **Email**: Standard inbox

### Monitoring Alerts (<12 signals)
- **Discord**: Optional, database only
- **Slack**: Suppressed
- **Telegram**: None
- **Email**: Digest summary

## Compliance and Best Practices

1. **Alert Fatigue Prevention**
   - Limit to 20-30 alerts per day maximum
   - Use tiered watchlists
   - Adjust thresholds to reduce noise

2. **Documentation**
   - Log all alert configurations
   - Track changes to thresholds
   - Document rationale for adjustments

3. **Risk Disclosure**
   - Alerts are suggestions, not financial advice
   - Always perform due diligence
   - Respect position sizing limits

4. **System Reliability**
   - Monitor webhook uptime (>99.5%)
   - Test backup notification channels
   - Regular alert functionality checks

## Troubleshooting

### No Alerts Triggering
- Check signal threshold isn't too high
- Verify symbols are liquid and active
- Ensure alert hasn't expired

### Too Many Alerts
- Increase signal threshold
- Add volume filters
- Reduce watchlist size

### Delayed Alerts
- Check webhook response time
- Verify TradingView alert is "Once Per Bar Close"
- Monitor API rate limits

### Missing Enrichment Data
- Verify API keys are valid
- Check API rate limits
- Review data source status pages
