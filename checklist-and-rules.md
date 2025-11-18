# STB Toolkit - Checklist and Trade Rules

Version: 1.0  
Author: kozi214421 / Copilot-assisted  
Date: 2025-11-18

---

## Pre-Trade Checklist

### Setup Validation
- [ ] Indicator installed and configured in TradingView
- [ ] Alert thresholds set (Score 6, 10, 14)
- [ ] Webhook enrichment configured (if using automation)
- [ ] Manual flags updated (short interest, options flow, dark pool)
- [ ] Market regime confirmed (SPY/QQQ above 20 EMA or breadth positive)

### Signal Confirmation (Core 8)
- [ ] **Breakout**: Price clearly above resistance level
- [ ] **Volume**: Volume > 1.8× 20-bar average
- [ ] **EMA Stack**: 9 > 20 > 50 and price above all EMAs
- [ ] **RSI**: RSI > 60 (momentum confirmation)
- [ ] **BB Release**: Bollinger Band squeeze releasing (if present)
- [ ] **MACD**: Bullish cross above zero (if present)
- [ ] **Higher Lows**: Clear ascending low structure
- [ ] **Candle**: Breakout candle wide-range, close near high

### Advanced Signal Enhancement (Optional but Recommended)
- [ ] **VBP Shelf**: High-volume support zone below price
- [ ] **Air Pocket**: Low-volume zone above (room to run)
- [ ] **Relative Strength**: Outperforming market/sector by >5%
- [ ] **Short Interest**: SI% > 10% and DTC > 2 (squeeze potential)
- [ ] **Options Flow**: Unusual bullish options activity
- [ ] **AVWAP**: Price reclaiming anchored VWAP
- [ ] **Dark Pool**: Institutional buying detected
- [ ] **VCP**: Volatility contraction followed by expansion
- [ ] **Inside Pattern**: Inside bar/week breakout
- [ ] **Accumulation**: Diminishing pullback volume + higher lows
- [ ] **Tape Reading**: Down-volume drying, up-volume strengthening

### Risk Assessment
- [ ] Stop loss level identified (breakout low / EMA9 / ATR-based)
- [ ] Risk per trade ≤ 1.0% of portfolio
- [ ] Position size calculated (risk_amount / stop_distance)
- [ ] Target 1 calculated (consolidation range × 1.0)
- [ ] Target 2 calculated (consolidation range × 2.0)
- [ ] Not exceeding max concurrent breakout trades (3 recommended)

### Timing Considerations
- [ ] Entry during optimal time window (first 2 hours for intraday)
- [ ] Avoid major news events in next 30-60 minutes
- [ ] Check for earnings announcements (unless playing the catalyst)
- [ ] Confirm adequate liquidity (avg daily volume > 500K for stocks)

---

## Entry Rules

### Primary Breakout Entry
**Trigger**: Close of breakout candle with score ≥ 6

**Conditions**:
1. Price breaks and closes above resistance
2. Volume expansion (>1.5× average)
3. EMA stack aligned (bullish)
4. Score ≥ 6 (≥10 for conservative entries)
5. Market regime filter passed (SPY/QQQ above 20 EMA)

**Execution**:
- Enter at market close or next bar open
- Set stop immediately upon entry
- Place GTC orders for targets if using automation

### Alternative: Pullback Entry
**Trigger**: Pullback to EMA9/20 or AVWAP with volume support

**Conditions**:
1. Previous breakout occurred (score was ≥6)
2. Price pulls back to EMA9, EMA20, or AVWAP
3. Volume on pullback diminishing
4. Volume picks up on bounce from support
5. Score still ≥ 5 on pullback

**Execution**:
- Enter at support level with tight stop
- More conservative than breakout entry
- Better risk/reward ratio

---

## Stop Loss Rules

### Option 1: Breakout Low Stop (Tight)
- Set stop 1-2 ticks below breakout candle low
- Pros: Minimizes loss on fakeouts
- Cons: May get stopped on normal volatility

### Option 2: EMA9 Stop (Moderate)
- Set stop 1-3% below EMA9
- Pros: Gives trade room to breathe
- Cons: Larger loss if invalidated

### Option 3: ATR-Based Stop (Dynamic)
- Set stop at entry - (ATR × 1.25 to 1.5)
- Pros: Adjusts to volatility
- Cons: May be too wide on low-volatility names

**Stop Management**:
- Never widen stops after entry
- Trail stop to breakeven after +1R gain
- Trail with EMA9 after +2R gain
- Use mental stops for large positions to avoid stop-hunting

---

## Profit Target Rules

### Target 1: Scale Out (50%)
**Price**: Entry + (consolidation range × 1.0)

**Action**:
- Close 50% of position
- Lock in profits
- Reduce pressure on remaining position

### Target 2: Runner Exit
**Price**: Entry + (consolidation range × 2.0)

**Action**:
- Close remaining 50% OR
- Trail with EMA9 (close if price closes below EMA9)
- Use 0.5× ATR trailing stop for extended runs

### Extended Runner Management
- After +3R gain: trail with EMA9 only
- Move stop to breakeven + 2R minimum
- Let winner run if all signals remain bullish
- Close immediately if score drops below 3

---

## Position Sizing Rules

### Risk-Based Sizing (Recommended)
```
Risk Amount = Portfolio × (Risk% / 100)
Stop Distance = Entry Price - Stop Price
Position Size = Risk Amount / Stop Distance
```

**Example**:
- Portfolio: $100,000
- Risk per trade: 1.0% = $1,000
- Entry: $50.00
- Stop: $48.00 (distance = $2.00)
- Position Size = $1,000 / $2.00 = 500 shares

### Percent of Portfolio Sizing (Alternative)
- Use 5-10% of portfolio per position
-适用 for high-confidence setups (score ≥12)
- Maximum 3 concurrent positions

### Kelly Criterion (Advanced)
```
Kelly% = (Win Rate × Avg Win - Loss Rate × Avg Loss) / Avg Win
Position Size = Portfolio × (Kelly% × 0.5)  // Use half-Kelly for safety
```

---

## Trade Management Rules

### First 30 Minutes After Entry
- Monitor closely for confirmation
- Volume should remain elevated (>1.2× avg)
- Price should not immediately fail back below entry
- If fakeout apparent, exit immediately

### First Hour to First Day
- Price should be holding above EMA9
- No significant volume selling
- Score should remain ≥5
- Trail stop to breakeven after +1R

### Multi-Day Holds
- Review score daily
- Exit if score drops below 3 for 2 consecutive closes
- Exit if market regime deteriorates (SPY/QQQ break below 50 EMA)
- Scale out on exhaustion gaps or parabolic moves

### When to Add to Position
- On pullback to EMA9/20 with score ≥7
- Maximum 2 adds per position
- Each add must have same risk as initial entry
- Never add to losing positions

---

## Risk Management Framework

### Per-Trade Limits
- Maximum risk per trade: 1.0% of portfolio
- Preferred risk per trade: 0.5% for new setups
- Increase to 1.0% for proven high-confidence patterns

### Portfolio Limits
- Maximum concurrent breakout trades: 3
- Maximum sector concentration: 40%
- Maximum portfolio drawdown before pause: 6%
- Maximum daily loss before pause: 2%

### Win/Loss Management
- After 3 consecutive losses: reduce position size by 50%
- After 5 consecutive wins: take day/week off to reset
- Review and journal all trades (win or lose)
- Monthly strategy review and parameter tuning

---

## Automation Rules (If Using Webhook)

### Auto-Execute Criteria
- Score ≥ 10 (strong breakout)
- All external data enriched (SI%, options, dark pool)
- Market regime filter passed
- Position limits not exceeded
- Time window appropriate (9:30-11:30 AM ET for intraday)

### Manual Review Required
- Score 6-9 (borderline setups)
- Conflicting signals (e.g., high SI% but no options flow)
- Near market close (after 3:00 PM ET)
- High recent volatility (VIX > 30)

### Blackout Periods (No Auto-Execute)
- First/last 5 minutes of trading day
- FOMC announcement days
- Major economic data releases
- Stock earnings days (unless playing the catalyst)

---

## Journaling Template

### Pre-Trade
- Date/Time: _______
- Ticker: _______
- Score: _______
- Active Signals: _______
- Entry Price: _______
- Stop: _______
- Target 1/2: _______
- Position Size: _______
- Risk Amount: $______
- Market Regime: [ ] Bullish [ ] Neutral [ ] Bearish

### During Trade
- Initial reaction (first 30 min): _______
- Peak profit: _______
- Max adverse excursion: _______
- Emotional state: [ ] Calm [ ] Anxious [ ] Excited [ ] Fearful

### Post-Trade
- Exit Price: _______
- Exit Reason: [ ] Target [ ] Stop [ ] Trailing Stop [ ] Discretionary
- P/L: $______ (____R)
- What worked: _______
- What didn't work: _______
- Lessons learned: _______
- Would I take this trade again: [ ] Yes [ ] No [ ] With modifications

---

## Score Interpretation Guide

### Score 0-5: Weak Setup
**Action**: Pass or monitor only
- Insufficient confirmation
- High fakeout risk
- Wait for more signals to align

### Score 6-9: Moderate Setup
**Action**: Small position or pullback entry
- Acceptable risk/reward
- Requires tight risk management
- Consider waiting for pullback to EMAs

### Score 10-13: Strong Setup
**Action**: Standard position size
- High-probability setup
- Multiple confirmations
- Good risk/reward ratio
- Primary entry at breakout

### Score 14-20: Institutional-Grade Setup
**Action**: Maximum position size (within limits)
- Very high probability
- Multiple institutional signals
- Exceptional risk/reward
- Consider adding on pullbacks

---

## Common Mistakes to Avoid

### Entry Mistakes
- [ ] Chasing price after breakout (enter on pullback instead)
- [ ] Ignoring market regime (don't fight the tape)
- [ ] Overtrading low-score setups (be patient)
- [ ] Entering during low-liquidity periods
- [ ] Ignoring extended price from EMAs

### Exit Mistakes
- [ ] Moving stops wider (never widen stops)
- [ ] Taking profits too early on high-score setups
- [ ] Holding through clear breakdown signals
- [ ] Averaging down on losing positions
- [ ] Not trailing stops on runners

### Risk Mistakes
- [ ] Position size too large (respect 1% rule)
- [ ] Too many concurrent trades (max 3)
- [ ] Ignoring portfolio heat (total risk exposure)
- [ ] Trading during emotional state
- [ ] Revenge trading after losses

---

## Monthly Review Checklist

### Performance Metrics
- [ ] Total trades: _______
- [ ] Win rate: _______%
- [ ] Average winner: $_______ (____R)
- [ ] Average loser: $_______ (____R)
- [ ] Profit factor: _______
- [ ] Maximum drawdown: _______%
- [ ] Sharpe ratio: _______
- [ ] Best/worst trade: $_______/$_______

### Score Analysis
- [ ] Average score of winning trades: _______
- [ ] Average score of losing trades: _______
- [ ] Win rate by score bucket:
  - Score 6-9: _______%
  - Score 10-13: _______%
  - Score 14-20: _______%

### Process Adherence
- [ ] Trades within rules: _______%
- [ ] Optimal entries: _______%
- [ ] Proper stop placement: _______%
- [ ] Target management: _______%
- [ ] Position sizing accuracy: _______%

### Adjustments for Next Month
- [ ] Parameter changes needed: _______
- [ ] Process improvements: _______
- [ ] Psychological improvements: _______
- [ ] Risk management updates: _______

---

## Emergency Protocols

### Portfolio Emergency Stop
**Trigger**: Portfolio drawdown reaches 6%

**Action**:
1. Close all positions immediately
2. Take 1-week break from trading
3. Review all recent trades
4. Identify systematic issues
5. Re-paper trade for 2 weeks before resuming

### Blown Stop
**Trigger**: Position loses >2× planned risk

**Action**:
1. Exit immediately (don't hope for recovery)
2. Reduce position size by 50% for next 5 trades
3. Review what caused violation
4. Update risk controls

### Technical Issues
**Trigger**: Platform/connectivity issues during trade

**Action**:
1. Call broker to manage position if needed
2. Have backup trading platform ready
3. Keep broker phone number accessible
4. Use limit orders instead of market orders

---

## Appendix: Quick Reference Card

### Entry Checklist (Essential Only)
1. Score ≥ 6
2. Volume > 1.5× avg
3. EMA stack bullish
4. Market regime bullish
5. Stop identified

### Exit Checklist
1. Target 1: Scale 50%
2. Target 2: Exit or trail
3. Stop: Never widen
4. Trail: EMA9 after +2R

### Risk Formula
```
Position Size = (Portfolio × Risk%) / (Entry - Stop)
```

### Contact for Emergencies
- Broker Phone: ______________
- Backup Platform: ______________
- Trading Partner: ______________

---

**Print this document and keep it accessible during trading hours.**

**Review before each trading session.**

**Update monthly based on performance review.**
