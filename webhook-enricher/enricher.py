"""
STB Webhook Enricher - Python/Flask Implementation

Receives TradingView alerts and enriches them with external data
(short interest, options flow, dark pool activity)
"""

import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'change-me-in-production')
IEX_TOKEN = os.getenv('IEX_TOKEN', '')
CHEDDAR_TOKEN = os.getenv('CHEDDAR_TOKEN', '')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK', '')

# In-memory cache with TTL
cache = {}
CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds


def log_event(level, event, data=None):
    """Structured logging"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'event': event
    }
    if data:
        log_entry.update(data)
    print(json.dumps(log_entry))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint"""
    try:
        alert = request.get_json()
        
        # Validate secret token
        if alert.get('secret') != SECRET_TOKEN:
            log_event('error', 'invalid_secret', {'ip': request.remote_addr})
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Validate required fields
        if not all(k in alert for k in ['ticker', 'price', 'score']):
            log_event('error', 'invalid_payload', alert)
            return jsonify({'error': 'Missing required fields'}), 400
        
        log_event('info', 'alert_received', {
            'ticker': alert['ticker'],
            'price': alert['price'],
            'score': alert['score']
        })
        
        # Respond quickly to TradingView
        response = jsonify({'status': 'received'})
        
        # Process alert (in production, use background task/queue)
        try:
            process_alert(alert)
        except Exception as e:
            log_event('error', 'processing_failed', {
                'error': str(e),
                'ticker': alert.get('ticker')
            })
        
        return response, 200
        
    except Exception as error:
        log_event('error', 'webhook_error', {'error': str(error)})
        return jsonify({'error': 'Internal server error'}), 500


def process_alert(alert):
    """Process and enrich alert"""
    ticker = alert['ticker']
    price = alert['price']
    score = alert['score']
    time_str = alert.get('time', '')
    interval = alert.get('interval', '')
    volume = alert.get('volume', 0)
    
    try:
        # Fetch enrichment data
        short_interest_data = get_short_interest(ticker)
        options_data = get_options_flow(ticker)
        dark_pool_data = get_dark_pool_activity(ticker)
        
        # Calculate enriched score
        enriched_score = calculate_enriched_score(
            score,
            short_interest_data,
            options_data,
            dark_pool_data
        )
        
        # Determine action
        action = determine_action(enriched_score)
        
        # Create enriched alert object
        enriched_alert = {
            'ticker': ticker,
            'price': price,
            'baseScore': score,
            'enrichedScore': enriched_score,
            'action': action['action'],
            'priority': action['priority'],
            'time': time_str,
            'interval': interval,
            'volume': volume,
            'enrichmentData': {
                'shortInterest': short_interest_data,
                'options': options_data,
                'darkPool': dark_pool_data
            }
        }
        
        log_event('info', 'alert_enriched', {
            'ticker': ticker,
            'baseScore': score,
            'enrichedScore': enriched_score,
            'action': action['action']
        })
        
        # Send notifications
        send_notifications(enriched_alert)
        
        # Execute trade if conditions met
        if action['action'] == 'EXECUTE':
            log_event('info', 'execute_signal', enriched_alert)
            # TODO: Implement trade execution logic
            # execute_trade(enriched_alert)
        
    except Exception as error:
        log_event('error', 'enrichment_error', {
            'error': str(error),
            'ticker': ticker
        })


def get_short_interest(ticker):
    """Fetch short interest data"""
    cache_key = f'si_{ticker}'
    
    # Check cache
    if cache_key in cache:
        cached = cache[cache_key]
        if time.time() - cached['timestamp'] < CACHE_TTL:
            return cached['data']
    
    try:
        if not IEX_TOKEN:
            return {
                'shortInterestPct': 0,
                'daysToCover': 0,
                'source': 'none'
            }
        
        # IEX Cloud API
        response = requests.get(
            f'https://cloud.iexapis.com/stable/stock/{ticker}/stats',
            params={'token': IEX_TOKEN},
            timeout=5
        )
        response.raise_for_status()
        
        stats = response.json()
        
        data = {
            'shortInterestPct': stats.get('shortRatio', 0),
            'daysToCover': (stats.get('shortInterest', 0) / stats.get('avg10Volume', 1)) 
                          if stats.get('avg10Volume') else 0,
            'source': 'iex'
        }
        
        # Cache result
        cache[cache_key] = {'data': data, 'timestamp': time.time()}
        
        return data
        
    except Exception as error:
        log_event('warn', 'short_interest_fetch_failed', {
            'ticker': ticker,
            'error': str(error)
        })
        return {
            'shortInterestPct': 0,
            'daysToCover': 0,
            'source': 'error'
        }


def get_options_flow(ticker):
    """Fetch options flow data"""
    try:
        if not CHEDDAR_TOKEN:
            return {
                'bullishSweeps': 0,
                'bearishSweeps': 0,
                'totalPremium': 0,
                'source': 'none'
            }
        
        # CheddarFlow API (example)
        response = requests.get(
            'https://api.cheddarflow.com/api/v1/sweeps',
            headers={'Authorization': f'Bearer {CHEDDAR_TOKEN}'},
            params={'symbol': ticker, 'age': '24h'},
            timeout=5
        )
        response.raise_for_status()
        
        sweeps = response.json() or []
        
        return {
            'bullishSweeps': len([s for s in sweeps if s.get('sentiment') == 'bullish']),
            'bearishSweeps': len([s for s in sweeps if s.get('sentiment') == 'bearish']),
            'totalPremium': sum(s.get('premium', 0) for s in sweeps),
            'source': 'cheddarflow'
        }
        
    except Exception as error:
        log_event('warn', 'options_flow_fetch_failed', {
            'ticker': ticker,
            'error': str(error)
        })
        return {
            'bullishSweeps': 0,
            'bearishSweeps': 0,
            'totalPremium': 0,
            'source': 'error'
        }


def get_dark_pool_activity(ticker):
    """Fetch dark pool activity (placeholder - vendor-specific)"""
    try:
        # This is a placeholder - implement with your dark pool data provider
        return {
            'buyVolume': 0,
            'sellVolume': 0,
            'netVolume': 0,
            'prints': 0,
            'source': 'none'
        }
        
    except Exception as error:
        log_event('warn', 'dark_pool_fetch_failed', {
            'ticker': ticker,
            'error': str(error)
        })
        return {
            'buyVolume': 0,
            'sellVolume': 0,
            'netVolume': 0,
            'prints': 0,
            'source': 'error'
        }


def calculate_enriched_score(base_score, short_interest, options, dark_pool):
    """Calculate enriched score based on external data"""
    enriched_score = base_score
    
    # Add points for high short interest + days to cover
    if short_interest['shortInterestPct'] > 10 and short_interest['daysToCover'] > 2:
        enriched_score += 2
    elif short_interest['shortInterestPct'] > 5 and short_interest['daysToCover'] > 1:
        enriched_score += 1
    
    # Add points for bullish options activity
    if options['bullishSweeps'] >= 5:
        enriched_score += 2
    elif options['bullishSweeps'] >= 3:
        enriched_score += 1
    
    # Subtract for bearish options activity
    if options['bearishSweeps'] > options['bullishSweeps'] * 2:
        enriched_score -= 1
    
    # Add points for dark pool buying
    if dark_pool['buyVolume'] > dark_pool['sellVolume'] * 1.5:
        enriched_score += 1
    
    return max(0, enriched_score)  # Ensure non-negative


def determine_action(enriched_score):
    """Determine action based on enriched score"""
    if enriched_score >= 14:
        return {'action': 'EXECUTE', 'priority': 'HIGH'}
    elif enriched_score >= 10:
        return {'action': 'EXECUTE', 'priority': 'MEDIUM'}
    elif enriched_score >= 8:
        return {'action': 'WATCH', 'priority': 'MEDIUM'}
    elif enriched_score >= 6:
        return {'action': 'WATCH', 'priority': 'LOW'}
    else:
        return {'action': 'IGNORE', 'priority': 'LOW'}


def send_notifications(alert):
    """Send notifications to configured channels"""
    if DISCORD_WEBHOOK:
        try:
            send_discord_notification(alert)
        except Exception as e:
            log_event('error', 'discord_notification_failed', {'error': str(e)})
    
    if SLACK_WEBHOOK:
        try:
            send_slack_notification(alert)
        except Exception as e:
            log_event('error', 'slack_notification_failed', {'error': str(e)})


def send_discord_notification(alert):
    """Send Discord notification"""
    color = 0x00ff00 if alert['action'] == 'EXECUTE' else \
            0xff9900 if alert['action'] == 'WATCH' else 0x808080
    
    payload = {
        'embeds': [{
            'title': f"{get_emoji(alert['action'])} STB Alert: {alert['ticker']}",
            'description': f"Enriched Score: **{alert['enrichedScore']}**/20 (Base: {alert['baseScore']})",
            'fields': [
                {'name': 'Price', 'value': f"${alert['price']:.2f}", 'inline': True},
                {'name': 'Action', 'value': alert['action'], 'inline': True},
                {'name': 'Priority', 'value': alert['priority'], 'inline': True},
                {'name': 'Short Interest', 
                 'value': f"{alert['enrichmentData']['shortInterest']['shortInterestPct']:.1f}%", 
                 'inline': True},
                {'name': 'Days to Cover', 
                 'value': f"{alert['enrichmentData']['shortInterest']['daysToCover']:.1f}", 
                 'inline': True},
                {'name': 'Options Sweeps', 
                 'value': f"{alert['enrichmentData']['options']['bullishSweeps']} bullish", 
                 'inline': True}
            ],
            'color': color,
            'timestamp': datetime.utcnow().isoformat(),
            'footer': {'text': f"STB Toolkit | {alert['interval']}"}
        }]
    }
    
    response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    response.raise_for_status()
    
    log_event('info', 'discord_notification_sent', {'ticker': alert['ticker']})


def send_slack_notification(alert):
    """Send Slack notification"""
    payload = {
        'text': f"STB Alert: {alert['ticker']}",
        'blocks': [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': f"{get_emoji(alert['action'])} {alert['ticker']} - {alert['action']}"
                }
            },
            {
                'type': 'section',
                'fields': [
                    {'type': 'mrkdwn', 'text': f"*Score:* {alert['enrichedScore']}/20 (Base: {alert['baseScore']})"},
                    {'type': 'mrkdwn', 'text': f"*Price:* ${alert['price']:.2f}"},
                    {'type': 'mrkdwn', 'text': f"*Priority:* {alert['priority']}"},
                    {'type': 'mrkdwn', 'text': f"*Interval:* {alert['interval']}"},
                    {'type': 'mrkdwn', 'text': f"*SI%:* {alert['enrichmentData']['shortInterest']['shortInterestPct']:.1f}%"},
                    {'type': 'mrkdwn', 'text': f"*DTC:* {alert['enrichmentData']['shortInterest']['daysToCover']:.1f}"},
                    {'type': 'mrkdwn', 'text': f"*Options:* {alert['enrichmentData']['options']['bullishSweeps']} bullish sweeps"}
                ]
            }
        ]
    }
    
    response = requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
    response.raise_for_status()
    
    log_event('info', 'slack_notification_sent', {'ticker': alert['ticker']})


def get_emoji(action):
    """Get emoji for action"""
    return {
        'EXECUTE': '🚀',
        'WATCH': '👀',
        'IGNORE': '📊'
    }.get(action, '📊')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    log_event('info', 'server_started', {'port': port})
    print(f'STB Webhook Enricher running on port {port}')
    app.run(host='0.0.0.0', port=port)
