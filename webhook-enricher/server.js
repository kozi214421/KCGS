/**
 * STB Webhook Enricher - Node.js/Express Implementation
 * 
 * Receives TradingView alerts and enriches them with external data
 * (short interest, options flow, dark pool activity)
 */

const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// Configuration
const PORT = process.env.PORT || 3000;
const SECRET_TOKEN = process.env.SECRET_TOKEN || 'change-me-in-production';
const IEX_TOKEN = process.env.IEX_TOKEN || '';
const CHEDDAR_TOKEN = process.env.CHEDDAR_TOKEN || '';
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK || '';
const SLACK_WEBHOOK = process.env.SLACK_WEBHOOK || '';

// In-memory cache for API results (with TTL)
const cache = new Map();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours for short interest

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

/**
 * Main webhook endpoint
 */
app.post('/webhook', async (req, res) => {
  try {
    const alert = req.body;
    
    // Validate secret token
    if (alert.secret !== SECRET_TOKEN) {
      logEvent('error', 'invalid_secret', { ip: req.ip });
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    // Validate required fields
    if (!alert.ticker || !alert.price || !alert.score) {
      logEvent('error', 'invalid_payload', alert);
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    logEvent('info', 'alert_received', {
      ticker: alert.ticker,
      price: alert.price,
      score: alert.score
    });
    
    // Respond quickly to TradingView
    res.status(200).json({ status: 'received' });
    
    // Process alert asynchronously
    processAlert(alert).catch(err => {
      logEvent('error', 'processing_failed', { error: err.message, ticker: alert.ticker });
    });
    
  } catch (error) {
    logEvent('error', 'webhook_error', { error: error.message });
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * Process and enrich alert
 */
async function processAlert(alert) {
  const { ticker, price, score, time, interval, volume } = alert;
  
  try {
    // Fetch enrichment data in parallel
    const [shortInterestData, optionsData, darkPoolData] = await Promise.all([
      getShortInterest(ticker),
      getOptionsFlow(ticker),
      getDarkPoolActivity(ticker)
    ]);
    
    // Calculate enriched score
    const enrichedScore = calculateEnrichedScore(
      score,
      shortInterestData,
      optionsData,
      darkPoolData
    );
    
    // Determine action
    const action = determineAction(enrichedScore);
    
    // Create enriched alert object
    const enrichedAlert = {
      ticker,
      price,
      baseScore: score,
      enrichedScore,
      action: action.action,
      priority: action.priority,
      time,
      interval,
      volume,
      enrichmentData: {
        shortInterest: shortInterestData,
        options: optionsData,
        darkPool: darkPoolData
      }
    };
    
    logEvent('info', 'alert_enriched', {
      ticker,
      baseScore: score,
      enrichedScore,
      action: action.action
    });
    
    // Send notifications
    await sendNotifications(enrichedAlert);
    
    // Execute trade if conditions met
    if (action.action === 'EXECUTE') {
      logEvent('info', 'execute_signal', enrichedAlert);
      // TODO: Implement trade execution logic
      // await executeTrade(enrichedAlert);
    }
    
  } catch (error) {
    logEvent('error', 'enrichment_error', { error: error.message, ticker });
  }
}

/**
 * Fetch short interest data
 */
async function getShortInterest(ticker) {
  const cacheKey = `si_${ticker}`;
  
  // Check cache
  if (cache.has(cacheKey)) {
    const cached = cache.get(cacheKey);
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data;
    }
  }
  
  try {
    if (!IEX_TOKEN) {
      return { shortInterestPct: 0, daysToCover: 0, source: 'none' };
    }
    
    // IEX Cloud API
    const response = await axios.get(
      `https://cloud.iexapis.com/stable/stock/${ticker}/stats`,
      {
        params: { token: IEX_TOKEN },
        timeout: 5000
      }
    );
    
    const data = {
      shortInterestPct: response.data.shortRatio || 0,
      daysToCover: response.data.shortInterest ? 
        (response.data.shortInterest / response.data.avg10Volume) : 0,
      source: 'iex'
    };
    
    // Cache result
    cache.set(cacheKey, { data, timestamp: Date.now() });
    
    return data;
    
  } catch (error) {
    logEvent('warn', 'short_interest_fetch_failed', { ticker, error: error.message });
    return { shortInterestPct: 0, daysToCover: 0, source: 'error' };
  }
}

/**
 * Fetch options flow data
 */
async function getOptionsFlow(ticker) {
  try {
    if (!CHEDDAR_TOKEN) {
      return { bullishSweeps: 0, bearishSweeps: 0, totalPremium: 0, source: 'none' };
    }
    
    // CheddarFlow API (example)
    const response = await axios.get(
      `https://api.cheddarflow.com/api/v1/sweeps`,
      {
        headers: { 'Authorization': `Bearer ${CHEDDAR_TOKEN}` },
        params: { 
          symbol: ticker,
          age: '24h'
        },
        timeout: 5000
      }
    );
    
    const sweeps = response.data || [];
    
    return {
      bullishSweeps: sweeps.filter(s => s.sentiment === 'bullish').length,
      bearishSweeps: sweeps.filter(s => s.sentiment === 'bearish').length,
      totalPremium: sweeps.reduce((sum, s) => sum + (s.premium || 0), 0),
      source: 'cheddarflow'
    };
    
  } catch (error) {
    logEvent('warn', 'options_flow_fetch_failed', { ticker, error: error.message });
    return { bullishSweeps: 0, bearishSweeps: 0, totalPremium: 0, source: 'error' };
  }
}

/**
 * Fetch dark pool activity (placeholder - vendor-specific)
 */
async function getDarkPoolActivity(ticker) {
  try {
    // This is a placeholder - implement with your dark pool data provider
    // Example: Quiver Quant, or other dark pool vendors
    
    return {
      buyVolume: 0,
      sellVolume: 0,
      netVolume: 0,
      prints: 0,
      source: 'none'
    };
    
  } catch (error) {
    logEvent('warn', 'dark_pool_fetch_failed', { ticker, error: error.message });
    return { buyVolume: 0, sellVolume: 0, netVolume: 0, prints: 0, source: 'error' };
  }
}

/**
 * Calculate enriched score based on external data
 */
function calculateEnrichedScore(baseScore, shortInterest, options, darkPool) {
  let enrichedScore = baseScore;
  
  // Add points for high short interest + days to cover
  if (shortInterest.shortInterestPct > 10 && shortInterest.daysToCover > 2) {
    enrichedScore += 2;
  } else if (shortInterest.shortInterestPct > 5 && shortInterest.daysToCover > 1) {
    enrichedScore += 1;
  }
  
  // Add points for bullish options activity
  if (options.bullishSweeps >= 5) {
    enrichedScore += 2;
  } else if (options.bullishSweeps >= 3) {
    enrichedScore += 1;
  }
  
  // Subtract for bearish options activity
  if (options.bearishSweeps > options.bullishSweeps * 2) {
    enrichedScore -= 1;
  }
  
  // Add points for dark pool buying
  if (darkPool.buyVolume > darkPool.sellVolume * 1.5) {
    enrichedScore += 1;
  }
  
  return Math.max(0, enrichedScore); // Ensure non-negative
}

/**
 * Determine action based on enriched score
 */
function determineAction(enrichedScore) {
  if (enrichedScore >= 14) {
    return { action: 'EXECUTE', priority: 'HIGH' };
  } else if (enrichedScore >= 10) {
    return { action: 'EXECUTE', priority: 'MEDIUM' };
  } else if (enrichedScore >= 8) {
    return { action: 'WATCH', priority: 'MEDIUM' };
  } else if (enrichedScore >= 6) {
    return { action: 'WATCH', priority: 'LOW' };
  } else {
    return { action: 'IGNORE', priority: 'LOW' };
  }
}

/**
 * Send notifications to configured channels
 */
async function sendNotifications(alert) {
  const notifications = [];
  
  // Discord notification
  if (DISCORD_WEBHOOK) {
    notifications.push(sendDiscordNotification(alert));
  }
  
  // Slack notification
  if (SLACK_WEBHOOK) {
    notifications.push(sendSlackNotification(alert));
  }
  
  await Promise.allSettled(notifications);
}

/**
 * Send Discord notification
 */
async function sendDiscordNotification(alert) {
  try {
    const color = alert.action === 'EXECUTE' ? 0x00ff00 : 
                  alert.action === 'WATCH' ? 0xff9900 : 0x808080;
    
    await axios.post(DISCORD_WEBHOOK, {
      embeds: [{
        title: `${getEmoji(alert.action)} STB Alert: ${alert.ticker}`,
        description: `Enriched Score: **${alert.enrichedScore}**/20 (Base: ${alert.baseScore})`,
        fields: [
          { name: 'Price', value: `$${alert.price.toFixed(2)}`, inline: true },
          { name: 'Action', value: alert.action, inline: true },
          { name: 'Priority', value: alert.priority, inline: true },
          { name: 'Short Interest', value: `${alert.enrichmentData.shortInterest.shortInterestPct.toFixed(1)}%`, inline: true },
          { name: 'Days to Cover', value: alert.enrichmentData.shortInterest.daysToCover.toFixed(1), inline: true },
          { name: 'Options Sweeps', value: `${alert.enrichmentData.options.bullishSweeps} bullish`, inline: true }
        ],
        color: color,
        timestamp: new Date().toISOString(),
        footer: { text: `STB Toolkit | ${alert.interval}` }
      }]
    });
    
    logEvent('info', 'discord_notification_sent', { ticker: alert.ticker });
    
  } catch (error) {
    logEvent('error', 'discord_notification_failed', { error: error.message });
  }
}

/**
 * Send Slack notification
 */
async function sendSlackNotification(alert) {
  try {
    await axios.post(SLACK_WEBHOOK, {
      text: `STB Alert: ${alert.ticker}`,
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: `${getEmoji(alert.action)} ${alert.ticker} - ${alert.action}`
          }
        },
        {
          type: 'section',
          fields: [
            { type: 'mrkdwn', text: `*Score:* ${alert.enrichedScore}/20 (Base: ${alert.baseScore})` },
            { type: 'mrkdwn', text: `*Price:* $${alert.price.toFixed(2)}` },
            { type: 'mrkdwn', text: `*Priority:* ${alert.priority}` },
            { type: 'mrkdwn', text: `*Interval:* ${alert.interval}` },
            { type: 'mrkdwn', text: `*SI%:* ${alert.enrichmentData.shortInterest.shortInterestPct.toFixed(1)}%` },
            { type: 'mrkdwn', text: `*DTC:* ${alert.enrichmentData.shortInterest.daysToCover.toFixed(1)}` },
            { type: 'mrkdwn', text: `*Options:* ${alert.enrichmentData.options.bullishSweeps} bullish sweeps` }
          ]
        }
      ]
    });
    
    logEvent('info', 'slack_notification_sent', { ticker: alert.ticker });
    
  } catch (error) {
    logEvent('error', 'slack_notification_failed', { error: error.message });
  }
}

/**
 * Get emoji for action
 */
function getEmoji(action) {
  switch (action) {
    case 'EXECUTE': return '🚀';
    case 'WATCH': return '👀';
    default: return '📊';
  }
}

/**
 * Structured logging
 */
function logEvent(level, event, data = {}) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    event,
    ...data
  }));
}

// Start server
app.listen(PORT, () => {
  logEvent('info', 'server_started', { port: PORT });
  console.log(`STB Webhook Enricher running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logEvent('info', 'server_shutdown', {});
  process.exit(0);
});
