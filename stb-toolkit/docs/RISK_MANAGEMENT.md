# STB Toolkit Risk Management Guide

## Overview

Effective risk management is crucial for long-term trading success. This guide outlines risk management principles, position sizing strategies, and stop-loss methodologies specifically designed for the STB Toolkit.

## Core Risk Principles

### 1. Never Risk More Than You Can Afford to Lose
- Maximum account risk per trade: 1-2%
- Maximum concurrent position exposure: 20-30% of account
- Emergency reserve: Keep 10-20% cash for opportunities

### 2. Position Sizing Formula

```
Position Size = (Account Size × Risk %) / (Entry Price - Stop Loss Price)
```

**Example:**
```
Account Size: $100,000
Risk Per Trade: 2% ($2,000)
Entry Price: $50.00
Stop Loss: $49.00 (2% below entry)
Position Size = $2,000 / ($50 - $49) = 2,000 shares
Position Value = 2,000 × $50 = $100,000 (use margin or adjust)

Adjusted for no margin:
Maximum shares = $100,000 / $50 = 2,000 shares
Actual risk = 2,000 × ($50 - $49) = $2,000 ✓
```

### 3. Risk-Reward Ratio

**Minimum Acceptable:** 1:2 (risk $1 to make $2)
**Target:** 1:3 or better

**Calculation:**
```
Entry: $50.00
Stop Loss: $49.00 (risk = $1.00)
Take Profit: $53.00 (reward = $3.00)
Risk-Reward: 1:3 ✓
```

## Signal-Based Risk Adjustment

### High Confidence Signals (16+ signals)
- **Position Size:** Standard (1-2% risk)
- **Stop Loss:** Tighter (1.5-2% from entry)
- **Take Profit:** More aggressive (3-4% from entry)
- **Holding Period:** Longer (3-7 days)

### Medium Confidence Signals (13-15 signals)
- **Position Size:** Standard (1-2% risk)
- **Stop Loss:** Standard (2-2.5% from entry)
- **Take Profit:** Standard (4-5% from entry)
- **Holding Period:** Medium (2-5 days)

### Lower Confidence Signals (10-12 signals)
- **Position Size:** Reduced (0.5-1% risk)
- **Stop Loss:** Wider (2.5-3% from entry)
- **Take Profit:** Conservative (2-3% from entry)
- **Holding Period:** Shorter (1-3 days)

## Stop Loss Strategies

### 1. Percentage-Based Stop Loss

**Configuration in Strategy:**
```pine
stop_loss_pct = 2.0  // 2% below entry for longs
```

**Pros:**
- Simple to calculate
- Consistent risk per trade
- Easy to backtest

**Cons:**
- Doesn't account for volatility
- May be too tight in volatile markets

**Best For:** Standard market conditions, liquid stocks

### 2. ATR-Based Stop Loss

**Formula:**
```pine
atr = ta.atr(14)
stop_loss = entry_price - (2 × atr)  // For long positions
```

**Pros:**
- Adapts to volatility
- Reduces false stop-outs
- Better for different securities

**Cons:**
- More complex
- May be too wide in calm markets

**Best For:** Volatile stocks, different timeframes

### 3. Support/Resistance Stop Loss

**Method:**
- Long: Place stop below recent swing low or support
- Short: Place stop above recent swing high or resistance

**Pros:**
- Logical price levels
- Avoids arbitrary stops
- Aligns with market structure

**Cons:**
- Risk may vary significantly
- Requires chart analysis

**Best For:** Swing trading, technical traders

### 4. Time-Based Stop Loss

**Rules:**
- Exit if signal hasn't worked within X bars
- Daily chart: Exit after 3-5 days
- Hourly chart: Exit after 10-15 hours

**Pros:**
- Frees up capital
- Reduces opportunity cost
- Clear exit rules

**Cons:**
- May exit before move completes
- Requires discipline

**Best For:** Active traders, scalpers

### 5. Trailing Stop Loss

**Configuration:**
```pine
use_trailing_stop = true
trailing_stop_pct = 1.5  // Trail by 1.5%
```

**Activation:**
- Activate after profit reaches 1.5-2%
- Trail by 50% of current profit

**Pros:**
- Locks in profits
- Lets winners run
- Reduces emotional decisions

**Cons:**
- May exit too early in strong trends
- Requires monitoring

**Best For:** Trending markets, position trades

## Take Profit Strategies

### 1. Fixed Target

**Standard Configuration:**
```pine
take_profit_pct = 4.0  // 4% above entry
```

**When to Use:**
- Ranging markets
- Short-term trades
- High frequency trading

### 2. Multiple Targets

**Scaling Out Strategy:**
```
25% position at +2% (quick profit)
25% position at +4% (primary target)
25% position at +6% (extended target)
25% position at trailing stop (let it run)
```

**Implementation:**
- Manually scale out
- Or use strategy with multiple exit orders

### 3. Signal-Based Exits

**Exit When:**
- Opposite signals reach threshold (bearish >= 10 for long)
- Volume decreases significantly
- Price crosses below VWAP (for longs)
- RSI reaches extreme (>70 for longs)

**Configuration:**
```pine
exit_signal_threshold = 10  // Lower than entry threshold
exit_long = bearish_signals >= exit_signal_threshold
```

### 4. Time-Based Exits

**Rules:**
- Exit EOD for day trades
- Exit after 5 days for swing trades
- Exit before earnings/major events

### 5. Volatility-Based Targets

**Formula:**
```pine
atr = ta.atr(14)
take_profit = entry_price + (3 × atr)  // 3 ATR profit target
```

**Pros:**
- Adapts to market conditions
- Realistic profit expectations

## Portfolio-Level Risk Management

### Maximum Concurrent Positions

**Conservative:** 3-5 positions
- Easier to manage
- More focused analysis
- Better risk control

**Moderate:** 6-10 positions
- Balanced diversification
- Manageable monitoring
- Standard for most traders

**Aggressive:** 11-15 positions
- High diversification
- Requires automation
- More time intensive

### Sector Diversification

**Guidelines:**
```
Maximum per sector: 30% of portfolio
Minimum sectors: 3-5
Avoid correlation: Check beta to market
```

**Example Allocation:**
```
Technology: 30%
Healthcare: 20%
Consumer: 20%
Financial: 15%
Industrial: 15%
```

### Correlation Management

**Strategy:**
- Limit highly correlated positions (>0.7 correlation)
- Max 2-3 positions in same industry
- Balance long/short exposure

**Tools:**
- Use correlation matrix
- Monitor sector ETFs
- Check beta to SPY

### Maximum Drawdown Limits

**Account-Level Rules:**
```
Daily Loss Limit: -2% of account
Weekly Loss Limit: -5% of account
Monthly Loss Limit: -10% of account
```

**Actions When Limit Hit:**
- Stop trading for the day/week/month
- Review strategy and execution
- Reduce position sizes by 50%
- Seek mentorship or professional help

## Market Condition Adjustments

### Bull Market
- **Risk Per Trade:** Standard (2%)
- **Position Size:** Full positions
- **Stop Loss:** Standard (2%)
- **Strategy:** Favor long signals

### Bear Market
- **Risk Per Trade:** Reduced (1%)
- **Position Size:** 50% positions
- **Stop Loss:** Tighter (1.5%)
- **Strategy:** Favor short signals or cash

### Ranging/Choppy Market
- **Risk Per Trade:** Reduced (1%)
- **Position Size:** 50% positions
- **Stop Loss:** Wider (2.5%)
- **Strategy:** Higher signal threshold (14+)

### High Volatility (VIX > 30)
- **Risk Per Trade:** Reduced (0.5-1%)
- **Position Size:** 25-50% positions
- **Stop Loss:** ATR-based
- **Strategy:** Be selective, increase threshold

### Low Volatility (VIX < 15)
- **Risk Per Trade:** Standard (2%)
- **Position Size:** Full positions
- **Stop Loss:** Percentage-based
- **Strategy:** Standard approach

## Special Situations

### Earnings Reports
- **Before Earnings:** Exit positions 1 day before
- **After Earnings:** Wait 1 day for volatility to settle
- **Earnings Play:** Only with reduced position size (0.5%)

### FOMC/Fed Announcements
- **Day Of:** Reduce positions by 50%
- **After:** Wait for reaction to complete
- **High Impact:** Be in cash if uncertain

### Gap Events
- **Gap Up (Long):** Take partial profits if gap > 3%
- **Gap Down (Long):** Re-evaluate stop loss
- **Gap Through Stop:** Accept the loss, don't chase

### Circuit Breakers / Market Halts
- **Do Not Enter:** New positions during extreme volatility
- **Existing Positions:** Use mental stops if system fails
- **After Halt:** Re-evaluate all positions

## Institutional Data Risk Factors

### Short Interest
- **High Short Interest (>20%):** Potential squeeze, but also risk
  - **Action:** Reduce position size by 25%
  - **Stop Loss:** Tighter (1.5%)
  
- **Low Short Interest (<5%):** Less squeeze risk
  - **Action:** Standard position size
  - **Stop Loss:** Standard (2%)

### Options Flow (Unusual Whales)
- **Large Bullish Flow:** Confirms long signals
  - **Action:** Can increase position size by 25%
  - **Stop Loss:** Standard
  
- **Large Bearish Flow:** Caution on long signals
  - **Action:** Reduce position size by 50%
  - **Stop Loss:** Tighter (1.5%)

### Dark Pool Activity
- **Large Dark Pool Prints:** Institutional accumulation
  - **Action:** Hold positions longer
  - **Stop Loss:** Wider (2.5%)
  
- **No Dark Pool Activity:** Less institutional interest
  - **Action:** Standard approach
  - **Stop Loss:** Standard (2%)

## Psychological Risk Management

### Emotional Control
1. **Stick to the System:** Don't override signals emotionally
2. **Accept Losses:** They're part of trading
3. **No Revenge Trading:** After a loss, follow the system
4. **Take Breaks:** After 3 consecutive losses
5. **Celebrate Wins Modestly:** Don't get overconfident

### Trading Journal
**Track:**
- Entry/Exit prices
- Signal count at entry
- Reason for trade
- Emotions during trade
- Lessons learned

**Review:**
- Weekly: Performance metrics
- Monthly: Strategy adjustments
- Quarterly: System optimization

### Common Mistakes to Avoid
1. ❌ Moving stop loss further away (hoping)
2. ❌ Increasing position size to recover losses
3. ❌ Ignoring stop losses
4. ❌ Trading without stops
5. ❌ Risking more than 2% per trade
6. ❌ Overtrading (>10 trades/day)
7. ❌ Trading during news events without preparation
8. ❌ Holding through earnings without plan

## Emergency Procedures

### Account Breach Protocol
**If account is hacked or compromised:**
1. Immediately close all positions
2. Change all passwords
3. Contact broker
4. Freeze trading until secured

### System Failure Protocol
**If webhook or alerts fail:**
1. Switch to manual monitoring
2. Reduce position sizes
3. Use broker alerts as backup
4. Fix technical issues before resuming normal trading

### Black Swan Event Protocol
**During extreme market events:**
1. Close all positions immediately
2. Assess market structure
3. Wait for stability (usually 1-3 days)
4. Re-enter with reduced risk

## Risk Management Checklist

**Before Each Trade:**
- [ ] Calculate position size based on risk %
- [ ] Set stop loss before entry
- [ ] Define take profit target
- [ ] Check correlation with existing positions
- [ ] Verify signal count meets threshold
- [ ] Confirm adequate volume
- [ ] Review any upcoming events (earnings, FOMC)

**Daily:**
- [ ] Review open positions
- [ ] Check stop losses are in place
- [ ] Monitor daily loss limit
- [ ] Update trading journal
- [ ] Review alert queue

**Weekly:**
- [ ] Calculate weekly P&L
- [ ] Review trade performance
- [ ] Adjust position sizes if needed
- [ ] Check drawdown levels
- [ ] Plan next week's watchlist

**Monthly:**
- [ ] Full strategy review
- [ ] Risk-adjusted returns calculation
- [ ] Win rate and profit factor analysis
- [ ] System optimization if needed
- [ ] Goal setting for next month

## Risk Metrics to Monitor

### Key Performance Indicators
```
Sharpe Ratio: > 1.5 (good), > 2.0 (excellent)
Max Drawdown: < 15% (target)
Win Rate: > 50% (minimum)
Profit Factor: > 1.5 (good), > 2.0 (excellent)
Average Win/Loss: > 2.0
Recovery Factor: > 3.0
```

### Warning Signs
- 5 consecutive losses: Reduce position size
- Monthly loss > 10%: Stop trading, review system
- Win rate < 40%: Increase signal threshold
- Average loss > average win: Improve exits

## Conclusion

Risk management is not optional—it's the foundation of successful trading. The STB Toolkit provides excellent signals, but without proper risk management, even the best signals can lead to losses. Always:

1. **Risk only 1-2% per trade**
2. **Use stop losses on every trade**
3. **Diversify across sectors**
4. **Monitor drawdown limits**
5. **Adjust to market conditions**
6. **Keep a trading journal**
7. **Review and optimize regularly**

Remember: **Protect your capital first, profits will follow.**
