# STB Toolkit Data Sources Documentation

## Overview

The STB Toolkit integrates multiple data sources to provide comprehensive market intelligence. This document details each data source, its purpose, API integration, and optimization strategies.

## Primary Data Source: TradingView

### What It Provides
- Real-time and historical price data
- Volume data
- Technical indicator calculations
- Alert generation and delivery

### API Integration
- **Type:** Pine Script (built-in)
- **Latency:** Real-time to 1-second delay
- **Cost:** Included with TradingView subscription
- **Rate Limits:** No API limits for personal use

### Data Quality
- **Accuracy:** Exchange-grade data
- **Completeness:** All major exchanges covered
- **Timeliness:** Near real-time
- **Reliability:** 99.9%+ uptime

### TradingView Plans Comparison

| Feature | Basic | Pro | Pro+ | Premium |
|---------|-------|-----|------|---------|
| Indicators/Chart | 3 | 5 | 10 | 25 |
| Alerts | 1 | 20 | 100 | 400 |
| Webhook Alerts | ❌ | ✅ | ✅ | ✅ |
| Strategy Testing | Limited | ✅ | ✅ | ✅ |
| **Recommended For STB** | ❌ | ✅ | ✅ | ✅ |

**Minimum Required:** Pro ($14.95/month)

## Institutional Data Sources

### 1. Short Interest Data (FINRA)

#### What It Provides
- Short interest positions
- Days to cover
- Short interest ratio
- Historical short interest trends

#### Why It Matters
- **Short Squeeze Potential:** High short interest + bullish signals = potential squeeze
- **Sentiment Indicator:** Shows institutional bearish bets
- **Risk Assessment:** Heavily shorted stocks have unique risks

#### API Integration

**Provider:** FINRA (Financial Industry Regulatory Authority)
```
Endpoint: https://api.finra.org/data/v1/short-interest
Method: GET
Authentication: API Key (Bearer token)
Rate Limit: 100 requests/hour
Cost: Free for basic, $49/month for real-time
```

**Setup:**
1. Register at https://www.finra.org/
2. Apply for API access
3. Generate API key
4. Set environment variable: `FINRA_API_KEY=your_key`

**Data Fields:**
```json
{
  "ticker": "AAPL",
  "short_interest": 125000000,
  "avg_daily_volume": 85000000,
  "days_to_cover": 1.47,
  "short_percent_of_float": 5.2,
  "short_percent_change": -3.5,
  "date": "2024-01-15"
}
```

**Update Frequency:** Bi-weekly (published twice per month)

**Interpretation:**
- **Low (<5%):** Normal, limited squeeze potential
- **Medium (5-15%):** Watch for catalyst
- **High (15-30%):** Significant squeeze potential
- **Extreme (>30%):** High risk/high reward

#### Alternative Providers
1. **Ortex** - Real-time short interest estimates
2. **S3 Partners** - Institutional-grade short data
3. **MarketBeat** - Aggregated short interest data

### 2. Options Flow Data (Unusual Whales)

#### What It Provides
- Large options transactions (>$100k premium)
- Unusual options activity
- Put/call ratio analysis
- Institutional options positioning

#### Why It Matters
- **Institutional Intent:** Big money positioning
- **Leverage Plays:** Large options = high conviction
- **Directional Bias:** Call vs put flow
- **Catalyst Detection:** Pre-earnings positioning

#### API Integration

**Provider:** Unusual Whales
```
Endpoint: https://api.unusualwhales.com/api/flow
Method: GET
Authentication: API Key
Rate Limit: 300 requests/hour
Cost: $49/month (Starter), $99/month (Pro)
```

**Setup:**
1. Subscribe at https://unusualwhales.com/
2. Navigate to Account → API
3. Generate API key
4. Set environment variable: `UNUSUAL_WHALES_API_KEY=your_key`

**Data Fields:**
```json
{
  "ticker": "TSLA",
  "timestamp": "2024-01-15T10:30:00Z",
  "type": "CALL",
  "strike": 250,
  "expiry": "2024-02-16",
  "premium": 500000,
  "sentiment": "BULLISH",
  "size": 1000,
  "underlying_price": 240.50,
  "volume": 5000,
  "open_interest": 15000
}
```

**Update Frequency:** Real-time (1-5 second delay)

**Interpretation:**
- **Large Calls (>$500k):** Bullish institutional bet
- **Large Puts (>$500k):** Bearish or hedge position
- **Near-term expiry + large premium:** High conviction
- **Deep OTM:** Lottery tickets or hedge

#### Alternative Providers
1. **FlowAlgo** - Options flow alerts
2. **BlackBoxStocks** - Real-time options tracking
3. **Cheddar Flow** - Institutional options tracker

### 3. Dark Pool Data (Quiver Quant)

#### What It Provides
- Off-exchange trading volume
- Large block transactions
- Dark pool percentage of total volume
- Institutional accumulation/distribution

#### Why It Matters
- **Institutional Activity:** Smart money positioning
- **Low Impact Trading:** Big players accumulating
- **Price Discovery:** Hidden supply/demand
- **Breakout Confirmation:** Accumulation before move

#### API Integration

**Provider:** Quiver Quantitative
```
Endpoint: https://api.quiverquant.com/beta/darkpool
Method: GET
Authentication: API Key
Rate Limit: 100 requests/hour
Cost: $50/month (Basic), $200/month (Premium)
```

**Setup:**
1. Sign up at https://www.quiverquant.com/
2. Subscribe to dark pool data
3. Generate API key
4. Set environment variable: `QUIVER_API_KEY=your_key`

**Data Fields:**
```json
{
  "ticker": "NVDA",
  "date": "2024-01-15",
  "dark_pool_volume": 5000000,
  "total_volume": 45000000,
  "dark_pool_percentage": 11.1,
  "avg_dark_pool_size": 500,
  "large_prints": [
    {
      "timestamp": "2024-01-15T14:23:00Z",
      "size": 10000,
      "price": 498.50
    }
  ]
}
```

**Update Frequency:** Daily (end of day), some real-time features

**Interpretation:**
- **High Dark Pool % (>10%):** Significant institutional interest
- **Large Prints (>10k shares):** Block trades, potential positioning
- **Increasing Dark Pool %:** Accumulation phase
- **Price vs Dark Pool:** Price down + high DP = accumulation

#### Alternative Providers
1. **FINRA ADF** - Free but aggregated
2. **Trade Reporting Facility** - Raw data
3. **Various Brokers** - Premium dark pool scanners

### 4. Institutional Ownership (SEC EDGAR)

#### What It Provides
- 13F filings (quarterly holdings)
- Institutional ownership percentages
- Changes in holdings quarter-over-quarter
- Top institutional holders

#### Why It Matters
- **Smart Money Positions:** See what big institutions hold
- **Ownership Trends:** Increasing/decreasing institutional interest
- **Confidence Indicator:** High ownership = confidence
- **Float Analysis:** High ownership = lower float = more volatile

#### API Integration

**Provider:** SEC EDGAR (Free Government Data)
```
Endpoint: https://www.sec.gov/cgi-bin/browse-edgar
Method: GET
Authentication: None (requires User-Agent header)
Rate Limit: 10 requests/second
Cost: Free
```

**Setup:**
1. No registration required
2. Use SEC's public API
3. Set User-Agent header to identify your application

**Data Fields:**
```json
{
  "ticker": "AAPL",
  "reporting_date": "2023-12-31",
  "total_institutional_shares": 8500000000,
  "percent_of_shares": 63.5,
  "total_institutions": 4235,
  "change_from_prior_quarter": 2.3,
  "top_holders": [
    {
      "name": "Vanguard Group Inc",
      "shares": 1234567890,
      "percent": 9.2,
      "change": 0.5
    }
  ]
}
```

**Update Frequency:** Quarterly (45 days after quarter end)

**Interpretation:**
- **High Institutional % (>60%):** Stable, lower volatility
- **Low Institutional % (<30%):** Higher retail, more volatile
- **Increasing Ownership:** Institutions accumulating
- **Decreasing Ownership:** Institutions selling

#### Alternative Providers
1. **Whale Wisdom** - Cleaner interface, paid
2. **Data Roma** - Free 13F aggregator
3. **GuruFocus** - Guru investor tracking

## Supplementary Data Sources

### 5. Fundamentals (Optional)

**Providers:**
- **Alpha Vantage:** Free API with fundamentals
- **Financial Modeling Prep:** Comprehensive fundamentals
- **IEX Cloud:** Real-time and fundamental data

**Use Cases:**
- Filter by market cap
- P/E ratio screening
- Revenue growth trends
- Earnings date calendar

### 6. News & Sentiment (Optional)

**Providers:**
- **News API:** General news aggregation
- **Benzinga:** Financial news API
- **Twitter API:** Social sentiment
- **Reddit API:** Retail sentiment (WallStreetBets)

**Use Cases:**
- Catalyst identification
- Sentiment scoring
- Event-driven trading
- Avoid negative news during entries

### 7. Economic Calendar (Optional)

**Providers:**
- **Trading Economics API**
- **ForexFactory** (scraped)
- **Investing.com** (scraped)

**Use Cases:**
- FOMC meeting dates
- CPI/inflation reports
- Employment data
- Earnings season timing

## Data Integration Architecture

### System Flow
```
TradingView Alert
    ↓
Webhook Handler (Python)
    ↓
Parallel API Calls:
    → FINRA (Short Interest)
    → Unusual Whales (Options Flow)
    → Quiver Quant (Dark Pool)
    → SEC EDGAR (Institutional)
    ↓
Data Enrichment & Caching
    ↓
Alert Filtering & Prioritization
    ↓
Notification Dispatch
    ↓
User / Trading System
```

### Caching Strategy

**Short Interest:**
- Cache Duration: 24 hours
- Reason: Only updates bi-weekly
- Storage: In-memory or Redis

**Options Flow:**
- Cache Duration: 5 minutes
- Reason: High frequency updates
- Storage: In-memory with LRU eviction

**Dark Pool:**
- Cache Duration: 1 hour
- Reason: Daily updates mostly
- Storage: In-memory or Redis

**Institutional:**
- Cache Duration: 30 days
- Reason: Quarterly updates
- Storage: Database or persistent cache

### Error Handling

**API Failure Strategy:**
```python
1. Primary API call
2. If fails, wait 1 second
3. Retry up to 3 times with exponential backoff
4. If all retries fail:
   - Use cached data if available
   - Log error
   - Continue with partial enrichment
5. Alert user of data source issues
```

## Data Costs Summary

### Minimal Setup (Free - $15/month)
- TradingView Pro: $14.95/month
- SEC EDGAR: Free
- **Total:** ~$15/month

### Standard Setup ($64 - $114/month)
- TradingView Pro: $14.95/month
- Unusual Whales Starter: $49/month
- Quiver Quant Basic: $50/month OR FINRA Basic: Free
- **Total:** $64-$114/month

### Professional Setup ($264 - $514/month)
- TradingView Premium: $59.95/month
- Unusual Whales Pro: $99/month
- Quiver Quant Premium: $200/month
- Ortex (short interest): $79/month
- News API: $50/month
- **Total:** $488/month

### Enterprise Setup ($1000+/month)
- TradingView Premium: $59.95/month
- Multiple data providers with redundancy
- Custom data integrations
- Real-time everything

## Data Quality & Reliability

### Validation Methods

**1. Cross-Reference:**
- Compare FINRA short interest with Ortex estimates
- Verify institutional ownership across multiple sources
- Check dark pool data against reported volume

**2. Sanity Checks:**
```python
# Example validation
if short_interest_percent > 100:
    log_warning("Invalid short interest data")
    use_cached_data()

if dark_pool_percent > 50:
    log_warning("Unusually high dark pool percentage")
    verify_data_source()
```

**3. Staleness Detection:**
```python
# Check data age
data_age_hours = (now - data_timestamp).total_seconds() / 3600
if data_age_hours > 48:
    log_warning("Stale data detected")
    attempt_refresh()
```

### Backup Strategies

**If Primary Source Fails:**
1. Use cached data with timestamp
2. Fall back to alternative provider
3. Continue with reduced enrichment
4. Alert user of data issues

**If All Sources Fail:**
1. Use base alert without enrichment
2. Log all failures for investigation
3. Send notification to admin
4. Continue monitoring for recovery

## Optimization Tips

### 1. Reduce API Calls
- Cache aggressively based on update frequency
- Batch requests when possible
- Use webhooks instead of polling where available

### 2. Prioritize Data Sources
```
Critical: TradingView (signals)
High Priority: Options flow (real-time intent)
Medium Priority: Short interest (squeeze potential)
Low Priority: Institutional ownership (quarterly)
```

### 3. Conditional Enrichment
- Only fetch institutional data for signals >15
- Skip dark pool for small-cap stocks
- Limit options flow to liquid underlyings

### 4. Rate Limit Management
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=3600)  # 100 calls per hour
def fetch_short_interest(ticker):
    # API call
    pass
```

## Compliance & Legal

### Data Usage Rights
- **TradingView:** Personal use only, no redistribution
- **FINRA:** Public data, free to use
- **Unusual Whales:** Per subscription terms
- **Quiver Quant:** Per subscription terms
- **SEC EDGAR:** Public data, free to use

### Attribution Requirements
- Credit data sources in any public reports
- Don't claim data as proprietary
- Follow each provider's terms of service

### Data Retention
- **Recommendation:** 90 days for enriched alerts
- **Legal Requirement:** None for personal trading
- **Best Practice:** Maintain audit trail for tax purposes

## Troubleshooting

### Common Issues

**Issue: API returns 401 Unauthorized**
- Check API key is set correctly
- Verify environment variable name
- Confirm subscription is active

**Issue: API returns 429 Too Many Requests**
- Respect rate limits
- Implement exponential backoff
- Upgrade API tier if needed

**Issue: Stale or missing data**
- Check data source status page
- Verify internet connectivity
- Review cache expiration settings

**Issue: Inconsistent data between sources**
- Normal for estimates (short interest)
- Use most recent/reliable source
- Document discrepancies

## Future Enhancements

### Planned Integrations
1. **Level 2 Order Book Data:** For liquidity analysis
2. **Crypto Data:** Extend to cryptocurrency markets
3. **Futures/Options Chains:** Full derivative analysis
4. **Global Markets:** International exchange data
5. **Alternative Data:** Satellite, credit card, web traffic

### Advanced Features
1. **Machine Learning Predictions:** Using historical enriched data
2. **Sentiment Analysis:** NLP on news/social media
3. **Pattern Recognition:** AI-powered technical analysis
4. **Risk Scoring:** Automated position risk assessment

## Resources

### Documentation Links
- [TradingView Pine Script Reference](https://www.tradingview.com/pine-script-reference/)
- [FINRA API Documentation](https://www.finra.org/finra-data)
- [Unusual Whales API Docs](https://unusualwhales.com/api)
- [Quiver Quant API Docs](https://www.quiverquant.com/api)
- [SEC EDGAR Guide](https://www.sec.gov/edgar/searchedgar/companysearch.html)

### Community Resources
- [r/algotrading](https://reddit.com/r/algotrading)
- [QuantConnect Forums](https://www.quantconnect.com/forum)
- [TradingView Scripts](https://www.tradingview.com/scripts/)
