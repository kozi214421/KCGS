# Short-Term Breakout Toolkit (STB)

Version: 1.0  
Author: kozi214421 / Copilot-assisted  
Date: 2025-11-18

A comprehensive toolbox for detecting high-probability short-term breakouts. Includes:
- A TradingView Pine Script indicator ("STB Extended") that evaluates up to 20 heuristic signals (original 8 + advanced signals) and computes a combined score.
- Guidance to convert the indicator into a backtestable strategy (strategy.* in Pine) and recommended rules for entries, exits, stops, sizing, and alerts.
- A webhook enrichment workflow (Node.js / Python) blueprint to automatically enrich TradingView alerts with external data (short interest, options flow, dark-pool signals) and flip the manual flags in the indicator.
- Printable checklist and tuning / risk management guidance.

This README documents how everything fits together, how to install and configure, recommended data sources, how to backtest, and next recommended steps.

## Table of Contents
- [Overview](#overview)
- [What the indicator measures (signals)](#what-the-indicator-measures-signals)
- [Files in this repo](#files-in-this-repository)
- [Install & setup (TradingView)](#install--setup-tradingview)
- [Inputs & manual flags](#inputs--manual-flags-what-to-fill)
- [Alerts & webhook payload examples](#alerts--webhook-payload-examples)
- [Backtesting & converting to strategy](#backtesting--converting-to-a-strategy)
- [Webhook enrichment (architecture + example)](#webhook-enrichment-architecture--example)
- [Data sources & vendors](#data-sources--vendors)
- [Tuning, risk management & trade rules](#tuning-risk-management--trade-rules)
- [Testing & validation checklist](#testing--validation-checklist)
- [FAQ](#faq)
- [Practical next steps](#practical-next-steps-recommended)
- [Changelog](#changelog)
- [License & credits](#license--credits)

---

## Overview

The STB toolkit is designed to identify short-term breakout setups with higher probability by combining technical, volume-profile, relative-strength, and institutional-accumulation signals. The scanner outputs a numeric score and visual helpers (EMA stack, AVWAP, VBP histogram, signal table). Use it to scan, alert, and trade breakouts on intraday or daily timeframes.

---

## What the indicator measures (signals)

### Core short-term signals (8):
1. **Price breaking above a key level** (recent resistance)
2. **Volume expansion on breakout** (volume spike vs moving average)
3. **EMA stacking** (9 > 20 > 50 and price above them)
4. **RSI momentum threshold** (> ~60)
5. **Bollinger Band squeeze then release** (BB width breakout)
6. **MACD bullish cross above zero**
7. **Higher-low structure** prior to breakout
8. **Breakout-candle structure** (wide-range, close near high, small wick)

### Advanced signals added (12, where feasible):
9. **Volume-by-Price (VBP) shelf below price** (high-volume node)
10. **Low-volume gap above price (VBP)** — "air pocket"
11. **Relative Strength vs market/sector benchmark** (RS new highs)
12. **Short-interest and Days-to-Cover** (manual numeric inputs)
13. **Options flow** (manual boolean / enriched by webhook)
14. **Anchored VWAP (AVWAP) reclaim and pullback** (approximate)
15. **Dark-pool buying** (manual boolean / enriched)
16. **Volatility Contraction Pattern (VCP heuristic)**
17. **Inside-day / inside-week pattern**
18. **Liquidity vacuum** (thin VBP above price)
19. **Institutional accumulation heuristics** (diminishing pullback volume + higher lows)
20. **Tape-reading heuristics** (down-volume drying, rallies gaining strength)

### Notes on feasibility
- Pine Script cannot fetch options flow, exchange short-interest, dark-pool prints, or order-book depth. The indicator includes manual inputs for these signals; a webhook can auto-enrich them.
- Native TradingView VPVR is not accessible to Pine scripts. The indicator approximates VBP by bucketizing recent prices and summing volumes.

---

## Files in this repository

- **short-term-breakout-extended.pine**
  - TradingView Pine v5 indicator. Computes signals, score, plots EMAs, AVWAP (approx), VBP histogram (approx), and a signals table. Adds alertconditions for configurable score thresholds.
- **short-term-breakout-strategy.pine**
  - Strategy conversion. Contains entry/exit logic, position sizing examples, stop/target rules. Use for backtesting and optimization.
- **webhook-enricher/**
  - Example Node.js and Python scripts to receive TradingView alerts, enrich them with external APIs (short interest, options sweeps), then forward enriched alerts or call a TradingView-compatible webhook to record flags.
- **README.md** (this file)
- **checklist-and-rules.md** (printable checklist & trade rules)

---

## Install & setup (TradingView)

1. Open TradingView.
2. In the Pine editor, create a new script and paste the contents of `short-term-breakout-extended.pine`.
3. Save and Add to Chart.
4. Configure inputs:
   - Resistance lookback, volume MA length, EMA lengths (9/20/50), RSI length/threshold, BB settings, VBP lookback & bins.
   - For AVWAP anchoring, set anchor bars ago (or anchor manually by re-anchoring in your own AVWAP indicator if you prefer precise bar-time anchoring).
5. For manual inputs:
   - Short interest % and days-to-cover (fill from your data source).
   - Toggle options/dark-pool/order-flow booleans if you have external confirmations.
6. Place alerts:
   - Use the built-in alertconditions in the script:
     - Breakout (>= alert_score1)
     - Strong Breakout (>= alert_score2)
     - Institutional-grade Breakout (>= alert_score3)
   - Configure alerts to POST a JSON payload to your webhook endpoint for automation/enrichment.

---

## Inputs & manual flags (what to fill)

- **short_interest_pct**: manual numeric (enter latest SI% from your provider)
- **days_to_cover**: manual numeric (enter latest DTC)
- **options_bullish_flag**: manual boolean (or set by webhook)
- **dark_pool_buys**: manual boolean (or set by webhook)
- **orderflow_bullish**: manual boolean (or set by webhook)
- **avwap_anchor_bars**: integer offset to approximate anchoring (see script notes)

---

## Alerts & webhook payload examples

### TradingView alert message (example plain JSON):
```json
{
  "ticker": "{{ticker}}",
  "price": "{{close}}",
  "time": "{{time}}",
  "score": "{{plot_0}}",
  "signal_table": "see indicator values",
  "manual_flags": {
    "short_interest_pct": 12.3,
    "days_to_cover": 2.4,
    "options_bullish": true,
    "dark_pool_buys": false
  }
}
```

### Recommended alert flow:
1. Immediate alert on score >= alert_score1 (e.g., 6).
2. Follow-through alert: volume on next bar > 1.2 × breakout volume (confirm run).
3. Webhook receives the first alert, enriches with latest short-interest/options/dp prints, and evaluates whether to promote alert to "execute" or "watch" (see webhook section).

---

## Backtesting & converting to a strategy

### Goal: 
Convert the indicator into a Pine strategy script to backtest entries/exits and position sizing.

### Suggested entry rules:
- **Primary entry**: at close of breakout candle if score >= S_entry (e.g., 6).
- **Alternative (pullback) entry**: on pullback to 9/20 EMA or AVWAP with volume pickup and score >= S_pull (e.g., 5).
- **Stop**:
  - Tight: below breakout candle low or below 9 EMA.
  - Dynamic: ATR(14) * 1.25–1.5.
- **Targets**:
  - Target 1: consolidation range × 1.0
  - Target 2: consolidation range × 2.0 (let runner use trailing stop)
- **Position sizing**:
  - Risk percent per trade (0.25%–1.0%) or fixed dollar risk.
  - Position size = risk_amount / (entry - stop).

### How to build the strategy:
1. Duplicate the indicator code to a new Pine v5 script.
2. Replace `indicator()` with `strategy()` and implement `strategy.entry()` and `strategy.close()` calls.
3. Use `strategy.risk.max_drawdown` or manual position checks for risk limits.
4. Add strategy inputs for entry/stop/target percentages and backtest across multiple timeframes and tickers.
5. Log per-trade metrics via strategy.closedtrades.* and export results.

### Important strategy testing tips:
- Test across market regimes and multiple tickers (large-cap, mid-cap, ETFs).
- Walk-forward testing or rolling-window validation reduces curve-fitting.
- Keep parameter changes minimal and focus on process robustness.

---

## Webhook enrichment (architecture + example)

### Purpose: 
Automatically provide the indicator the external signals it cannot fetch (short-interest, options/darkpool, orderflow).

### Architecture:
1. TradingView alert POSTs JSON to your webhook public endpoint (e.g., AWS API Gateway / Lambda, Heroku, Vercel serverless, or ngrok during dev).
2. Webhook receives alert → extracts ticker and timestamp.
3. Webhook fetches latest external data:
   - Short interest & days-to-cover from data API (IEX Cloud / Fintel / Alpaca / Exchange)
   - Options sweeps from provider (FlowAlgo / CheddarFlow / your broker)
   - Dark-pool prints from your vendor or subscription
4. Webhook assembles enriched payload and:
   - Stores in DB / notifies you
   - Optionally calls a separate endpoint that writes the manual flags back into a dashboard or triggers an execute webhook (your order routing system)
   - Optionally re-posts an enriched TradingView-compatible payload to another internal endpoint

### Simple Node.js (Express) example (pseudo):
- Receive alert.
- Call IEX Cloud / Fintel for SI, DTC.
- Call options scanner API for sweep counts.
- Aggregate and send enriched message (email/Slack/Discord) and tag as EXECUTE if thresholds met.

### Security:
- Secure webhook with a secret token in headers.
- Validate TradingView's payload signature (if using).
- Rate-limit external API calls (cache short-interest daily).

### Example enrichment rules:
- If short_interest_pct >= 10 AND days_to_cover >= 2 AND options_sweeps_last_24h >= 3 → set options_bullish_flag = true.
- If dark-pool buys > threshold → dark_pool_buys = true.

---

## Data sources & vendors

### Short-interest / Days-to-cover:
- Fintel (fintel.io)
- IEX Cloud
- Nasdaq Data (official)
- S3 / vendors that publish exchange SI files

### Options flow:
- CheddarFlow
- FlowAlgo
- TradeTheFlow
- Your broker's options flow endpoint (if available)

### Dark pool / block prints:
- S3 datasets; dark pool vendors (subscription)
- Some brokers provide dark pool print tags

### Order-flow / Time-and-Sales / DOM:
- Bookmap (paid)
- NinjaTrader / Sierra Chart (with data feed)
- Broker DOMs and T&S via API

---

## Tuning, risk management & trade rules

### Parameter guidance:
- **Volume multiplier (breakout)**: 1.5–2.5× 20-bar avg (higher for illiquid names)
- **Resistance lookback**: intraday 10–30 bars, daily 20–60 days
- **RSI threshold**: 55–65 for early entries; 60+ for stronger momentum
- **BB squeeze sensitivity**: tune squeeze_mult and lookback to avoid being overly sensitive on small tickers

### Trade management:
- **Entry**: breakout close with score >= 6; prefer morning breakouts (first 120 minutes intraday)
- **Stop**: breakout low / 9 EMA / ATR-based
- **Scaling**: add to position on confirmed second volume bar or pullback to EMAs with support
- **Profit taking**: scale out 1/3–1/2 at first target, trail remainder with 9 EMA or 0.5× ATR

### Risk controls:
- Per-trade risk cap: 0.5–1.0% of portfolio
- Max concurrent breakout trades (configurable; e.g., 3)
- Market regime filter: only take breakouts if SPY/QQQ above 20/50 EMA or breadth is positive

---

## Testing & validation checklist

- [ ] Backtest on 100+ tickers across at least 3 market regimes.
- [ ] Record performance grouped by score bucket (6–9, 10–13, 14–20).
- [ ] Compute:
  - Win rate, average return, average drawdown, expectancy, max DD, Sharpe
  - False-positive (fakeout) rate = breakouts that printed > -stop before hitting first target
- [ ] Validate manual flags vs actual vendor data for several cases (short-interest, options sweep).
- [ ] Walk-forward test or out-of-sample test for at least 6 months.

---

## FAQ

**Q: Can the script auto-fetch short-interest and options flow?**  
A: Not from TradingView Pine. Use the webhook enrichment to automate the manual flags.

**Q: Is the VBP identical to TradingView VPVR?**  
A: No. The script approximates VBP by binning recent prices and summing volumes. Use native VPVR for precise visual, but it isn't accessible programmatically in Pine.

**Q: How should I set alert thresholds?**  
A: Start with moderate thresholds:
- Entry alert_score1 = 6 (consider entry)
- Strong alert_score2 = 10
- Institutional alert_score3 = 14
Tune based on backtesting.

**Q: Can I run live orders from these alerts?**  
A: Yes — but only after you implement safe order routing. Enriched webhook can decide whether to auto-execute or notify manually. Use a broker API with order throttling and pre-trade size checks.

---

## Practical next steps (recommended)

1. Install the indicator in TradingView and run in visual mode on several tickers/timeframes.
2. Create a simple strategy conversion and backtest with conservative filters (market regime, liquidity).
3. Implement webhook enricher (Node.js or Python) to fetch short-interest & options flow and forward enriched alerts.
4. Run a small paper-trade or simulation with the final strategy for 30–90 days before live money.

---

## Changelog

**1.0 — 2025-11-18**
- Initial combined indicator (20 heuristics) + README and usage guidance.

---

## License & credits

- MIT License (you may change as desired)
- Credits:
  - Trading concepts inspired by Mark Minervini (VCP), institutional tape-reading practices, and common breakout heuristics.
  - Copilot-assisted code and documentation.

---

## Contact / Support

Author: kozi214421  

If you want me to:
- Convert the indicator into a fully backtestable Pine strategy file (I can generate the script and initial parameter set)
- Provide the webhook Node.js and Python example code (complete webhook + enrichment + deploy notes)
- Integrate a simple demo that auto-enriches one ticker and posts to Discord/Slack with an "execute" recommendation

Tell me which of the above you want next and I will create the files (strategy script and webhook code) and include step-by-step deployment instructions and example API keys placeholders.
