# Webhook Enricher for STB Toolkit

This directory contains example implementations for automatically enriching TradingView alerts with external data sources.

## Overview

The webhook enricher receives TradingView alerts, fetches additional data (short interest, options flow, dark pool activity), and forwards enriched alerts to your notification system or trading platform.

## Architecture

```
TradingView Alert → Webhook Endpoint → Enrichment Logic → Notification/Execution
```

### Flow:
1. **TradingView** sends POST request with alert data
2. **Webhook** receives and validates the payload
3. **Enrichment** fetches external data from APIs
4. **Decision** evaluates enriched data against thresholds
5. **Action** sends notification or triggers trade execution

## Files

- **server.js** - Node.js/Express webhook server
- **enricher.py** - Python Flask webhook server
- **package.json** - Node.js dependencies
- **requirements.txt** - Python dependencies
- **.env.example** - Environment variable template
- **config.json** - Configuration template

## Setup

### Node.js Version

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run server**:
   ```bash
   npm start
   ```

4. **Deploy** (choose one):
   - **Heroku**: `git push heroku main`
   - **Vercel**: `vercel deploy`
   - **AWS Lambda**: Use serverless framework
   - **Local dev**: Use `ngrok http 3000`

### Python Version

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run server**:
   ```bash
   python enricher.py
   ```

4. **Deploy** (choose one):
   - **Heroku**: Use Procfile
   - **AWS Lambda**: Use Zappa
   - **Google Cloud Run**: Use Dockerfile
   - **Local dev**: Use `ngrok http 5000`

## TradingView Alert Setup

1. **Create Alert** in TradingView with the STB indicator
2. **Set Alert Condition**: Use the built-in alert conditions (score thresholds)
3. **Configure Webhook URL**: Enter your webhook endpoint
4. **Alert Message** (JSON format):

```json
{
  "ticker": "{{ticker}}",
  "price": {{close}},
  "time": "{{time}}",
  "interval": "{{interval}}",
  "score": {{plot("Total Score")}},
  "volume": {{volume}},
  "secret": "YOUR_SECRET_TOKEN"
}
```

## API Integrations

### Short Interest Data

**Option 1: IEX Cloud**
```javascript
const response = await fetch(`https://cloud.iexapis.com/stable/stock/${ticker}/stats?token=${IEX_TOKEN}`);
const data = await response.json();
const shortInterest = data.shortInterest;
const shortRatio = data.shortRatio;
```

**Option 2: Fintel** (requires subscription)
```javascript
const response = await fetch(`https://api.fintel.io/api/v1/shortInterest/${ticker}`, {
  headers: { 'X-API-KEY': FINTEL_KEY }
});
```

**Option 3: FINRA** (free but requires parsing)
```javascript
// Download FINRA short interest files
// Parse CNS files for ticker data
```

### Options Flow Data

**CheddarFlow API**:
```javascript
const response = await fetch(`https://api.cheddarflow.com/sweeps?symbol=${ticker}&age=24h`, {
  headers: { 'Authorization': `Bearer ${CHEDDAR_TOKEN}` }
});
const sweeps = await response.json();
const bullishSweeps = sweeps.filter(s => s.sentiment === 'bullish').length;
```

**FlowAlgo API** (requires subscription):
```javascript
const response = await fetch(`https://api.flowalgo.com/v1/flows/${ticker}`, {
  headers: { 'X-API-KEY': FLOWALGO_KEY }
});
```

### Dark Pool Data

**Example (vendor-specific)**:
```javascript
const response = await fetch(`https://api.darkpool-vendor.com/prints/${ticker}`, {
  headers: { 'Authorization': DARKPOOL_KEY }
});
const prints = await response.json();
const buyVolume = prints.filter(p => p.side === 'buy').reduce((sum, p) => sum + p.volume, 0);
```

## Enrichment Logic

### Example Decision Rules

```javascript
// Calculate enriched score
let enrichedScore = baseScore;

// Add points for short interest
if (shortInterestPct > 10 && daysToCover > 2) {
  enrichedScore += 2;
}

// Add points for options activity
if (bullishSweeps >= 3 && totalOptionsVolume > avgOptionsVolume * 2) {
  enrichedScore += 2;
}

// Add points for dark pool activity
if (darkPoolBuyVolume > darkPoolSellVolume * 1.5) {
  enrichedScore += 1;
}

// Decision
if (enrichedScore >= 12) {
  return { action: 'EXECUTE', priority: 'HIGH' };
} else if (enrichedScore >= 8) {
  return { action: 'WATCH', priority: 'MEDIUM' };
} else {
  return { action: 'IGNORE', priority: 'LOW' };
}
```

## Notification Integrations

### Discord Webhook
```javascript
await fetch(DISCORD_WEBHOOK_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    embeds: [{
      title: `🚀 STB Alert: ${ticker}`,
      description: `Score: ${enrichedScore}/20`,
      fields: [
        { name: 'Price', value: `$${price}`, inline: true },
        { name: 'Action', value: action, inline: true },
        { name: 'Short Interest', value: `${shortInterestPct}%`, inline: true },
        { name: 'Options Sweeps', value: bullishSweeps, inline: true }
      ],
      color: action === 'EXECUTE' ? 0x00ff00 : 0xff9900
    }]
  })
});
```

### Slack Webhook
```javascript
await fetch(SLACK_WEBHOOK_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: `STB Alert: ${ticker}`,
    blocks: [
      {
        type: 'section',
        text: { type: 'mrkdwn', text: `*${ticker}* - Score: ${enrichedScore}/20` }
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: `*Price:* $${price}` },
          { type: 'mrkdwn', text: `*Action:* ${action}` },
          { type: 'mrkdwn', text: `*SI%:* ${shortInterestPct}%` },
          { type: 'mrkdwn', text: `*Sweeps:* ${bullishSweeps}` }
        ]
      }
    ]
  })
});
```

### Email (SendGrid)
```javascript
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(SENDGRID_API_KEY);

await sgMail.send({
  to: RECIPIENT_EMAIL,
  from: SENDER_EMAIL,
  subject: `STB ${action}: ${ticker}`,
  html: `
    <h2>STB Breakout Alert</h2>
    <p><strong>Ticker:</strong> ${ticker}</p>
    <p><strong>Score:</strong> ${enrichedScore}/20</p>
    <p><strong>Action:</strong> ${action}</p>
    <p><strong>Price:</strong> $${price}</p>
    <p><strong>Short Interest:</strong> ${shortInterestPct}%</p>
    <p><strong>Options Sweeps (24h):</strong> ${bullishSweeps}</p>
  `
});
```

## Security Best Practices

1. **Authentication**: Use secret tokens in webhook payloads
2. **Rate Limiting**: Implement rate limiting (e.g., 10 requests/minute)
3. **Input Validation**: Validate and sanitize all inputs
4. **HTTPS Only**: Always use HTTPS for webhooks
5. **API Key Management**: Never commit API keys to version control
6. **IP Whitelisting**: Whitelist TradingView IPs if possible
7. **Logging**: Log all requests for debugging and audit

## Testing

### Test Webhook Locally

```bash
# Terminal 1: Start server
npm start

# Terminal 2: Send test request
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "price": 150.00,
    "time": "2025-11-18T10:30:00Z",
    "score": 8,
    "volume": 1000000,
    "secret": "YOUR_SECRET_TOKEN"
  }'
```

### Test with ngrok

```bash
# Terminal 1: Start server
npm start

# Terminal 2: Expose to internet
ngrok http 3000

# Use the ngrok HTTPS URL in TradingView
```

## Deployment Options

### Heroku
```bash
heroku create stb-webhook-enricher
heroku config:set IEX_TOKEN=your_token
heroku config:set SECRET_TOKEN=your_secret
git push heroku main
```

### Vercel (Serverless)
```bash
vercel deploy
vercel env add IEX_TOKEN
vercel env add SECRET_TOKEN
```

### AWS Lambda
```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
docker build -t stb-webhook-enricher .
docker run -p 3000:3000 -e IEX_TOKEN=xxx stb-webhook-enricher
```

## Monitoring

### Health Check Endpoint
```javascript
app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});
```

### Metrics to Track
- Total alerts received
- Enrichment success rate
- API call latency
- Error rate
- Alert action distribution (EXECUTE/WATCH/IGNORE)

### Logging
Use structured logging (JSON format) for easy parsing:
```javascript
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  level: 'info',
  event: 'alert_received',
  ticker: ticker,
  score: score,
  action: action
}));
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving alerts**
   - Check TradingView webhook URL
   - Verify server is running and accessible
   - Check firewall/security group settings

2. **API calls failing**
   - Verify API keys are correct
   - Check API rate limits
   - Ensure proper error handling

3. **Enrichment data stale**
   - Implement caching with TTL
   - Use cache for short interest (daily updates)
   - Don't cache options flow (real-time)

4. **High latency**
   - Make API calls in parallel (Promise.all)
   - Cache frequently accessed data
   - Use faster API endpoints

## Cost Considerations

### API Costs (Approximate)
- IEX Cloud: $9-99/month (depends on usage)
- CheddarFlow: $99-499/month
- FlowAlgo: $149-999/month
- SendGrid: Free tier for 100 emails/day
- Heroku: $7/month (hobby tier)

### Cost Optimization
- Cache short interest data (updates daily)
- Use free tier APIs when possible
- Batch API calls
- Implement smart filtering (only enrich high-score alerts)

## Next Steps

1. Choose your preferred implementation (Node.js or Python)
2. Sign up for required API services
3. Configure environment variables
4. Test locally with ngrok
5. Deploy to production
6. Configure TradingView alerts
7. Monitor and iterate

## Support

For issues or questions:
- Check the main README.md
- Review API provider documentation
- Test with curl/Postman before integrating
- Use logging to debug issues

---

**Remember**: Start with paper trading or notifications only before connecting to live order execution.
