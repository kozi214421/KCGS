#!/usr/bin/env python3
"""
STB Toolkit - Webhook Handler
Receives TradingView webhook alerts and enriches them with institutional data
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'webhook_config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)


class DataEnricher:
    """Enriches alert data with institutional information"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = {}
        
    def get_short_interest(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch short interest data"""
        if not self.config['data_enrichment']['short_interest']['enabled']:
            return None
            
        cache_key = f"short_interest_{ticker}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            cache_hours = self.config['data_enrichment']['short_interest']['cache_duration_hours']
            if time.time() - timestamp < cache_hours * 3600:
                return cached_data
        
        try:
            api_key = os.getenv(self.config['data_enrichment']['short_interest']['api_key_env'])
            if not api_key:
                logger.warning("Short interest API key not found")
                return None
                
            endpoint = self.config['data_enrichment']['short_interest']['api_endpoint']
            headers = {'Authorization': f'Bearer {api_key}'}
            params = {'ticker': ticker}
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            self.cache[cache_key] = (data, time.time())
            return data
            
        except Exception as e:
            logger.error(f"Error fetching short interest for {ticker}: {e}")
            return None
    
    def get_options_flow(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch unusual options activity"""
        if not self.config['data_enrichment']['options_flow']['enabled']:
            return None
            
        try:
            api_key = os.getenv(self.config['data_enrichment']['options_flow']['api_key_env'])
            if not api_key:
                logger.warning("Options flow API key not found")
                return None
                
            endpoint = self.config['data_enrichment']['options_flow']['api_endpoint']
            headers = {'Authorization': f'Bearer {api_key}'}
            
            lookback_hours = self.config['data_enrichment']['options_flow']['lookback_hours']
            min_premium = self.config['data_enrichment']['options_flow']['min_premium']
            
            params = {
                'ticker': ticker,
                'lookback_hours': lookback_hours,
                'min_premium': min_premium
            }
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching options flow for {ticker}: {e}")
            return None
    
    def get_dark_pool_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch dark pool trading data"""
        if not self.config['data_enrichment']['dark_pool']['enabled']:
            return None
            
        try:
            api_key = os.getenv(self.config['data_enrichment']['dark_pool']['api_key_env'])
            if not api_key:
                logger.warning("Dark pool API key not found")
                return None
                
            endpoint = self.config['data_enrichment']['dark_pool']['api_endpoint']
            headers = {'Authorization': f'Bearer {api_key}'}
            
            lookback_days = self.config['data_enrichment']['dark_pool']['lookback_days']
            params = {
                'ticker': ticker,
                'lookback_days': lookback_days
            }
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching dark pool data for {ticker}: {e}")
            return None
    
    def get_institutional_ownership(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch institutional ownership data"""
        if not self.config['data_enrichment']['institutional_ownership']['enabled']:
            return None
            
        try:
            endpoint = self.config['data_enrichment']['institutional_ownership']['api_endpoint']
            params = {
                'ticker': ticker,
                'lookback_quarters': self.config['data_enrichment']['institutional_ownership']['lookback_quarters']
            }
            
            response = requests.get(endpoint, params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching institutional data for {ticker}: {e}")
            return None
    
    def enrich_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich alert with all available institutional data"""
        ticker = alert_data.get('ticker', '').upper()
        
        enriched_data = {
            **alert_data,
            'enrichment_timestamp': datetime.utcnow().isoformat(),
            'institutional_data': {}
        }
        
        # Fetch short interest
        short_interest = self.get_short_interest(ticker)
        if short_interest:
            enriched_data['institutional_data']['short_interest'] = short_interest
        
        # Fetch options flow
        options_flow = self.get_options_flow(ticker)
        if options_flow:
            enriched_data['institutional_data']['options_flow'] = options_flow
        
        # Fetch dark pool data
        dark_pool = self.get_dark_pool_data(ticker)
        if dark_pool:
            enriched_data['institutional_data']['dark_pool'] = dark_pool
        
        # Fetch institutional ownership
        institutional = self.get_institutional_ownership(ticker)
        if institutional:
            enriched_data['institutional_data']['institutional_ownership'] = institutional
        
        return enriched_data


class AlertNotifier:
    """Sends notifications to various platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def send_discord(self, alert_data: Dict[str, Any]) -> bool:
        """Send notification to Discord"""
        if not self.config['notification_settings']['discord']['enabled']:
            return False
            
        try:
            webhook_url = self.config['notification_settings']['discord']['webhook_url']
            
            embed = {
                "title": f"STB Alert: {alert_data.get('signal', 'UNKNOWN')}",
                "description": f"Ticker: {alert_data.get('ticker', 'N/A')}",
                "color": 0x00ff00 if 'BUY' in alert_data.get('signal', '') else 0xff0000,
                "fields": [
                    {"name": "Price", "value": str(alert_data.get('price', 'N/A')), "inline": True},
                    {"name": "Signals", "value": str(alert_data.get('signals', 'N/A')), "inline": True},
                    {"name": "Time", "value": alert_data.get('time', 'N/A'), "inline": True}
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False
    
    def send_slack(self, alert_data: Dict[str, Any]) -> bool:
        """Send notification to Slack"""
        if not self.config['notification_settings']['slack']['enabled']:
            return False
            
        try:
            webhook_url = self.config['notification_settings']['slack']['webhook_url']
            channel = self.config['notification_settings']['slack']['channel']
            
            message = {
                "channel": channel,
                "text": f"STB Alert: {alert_data.get('signal', 'UNKNOWN')}",
                "attachments": [{
                    "color": "good" if 'BUY' in alert_data.get('signal', '') else "danger",
                    "fields": [
                        {"title": "Ticker", "value": alert_data.get('ticker', 'N/A'), "short": True},
                        {"title": "Price", "value": str(alert_data.get('price', 'N/A')), "short": True},
                        {"title": "Signals", "value": str(alert_data.get('signals', 'N/A')), "short": True}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=message, timeout=5)
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False
    
    def notify(self, alert_data: Dict[str, Any]) -> None:
        """Send notifications to all enabled platforms"""
        self.send_discord(alert_data)
        self.send_slack(alert_data)


# Initialize enricher and notifier
enricher = DataEnricher(config)
notifier = AlertNotifier(config)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.route('/api/stb-alerts', methods=['POST'])
def handle_alert():
    """Main webhook endpoint for TradingView alerts"""
    try:
        # Parse alert data
        alert_data = request.json
        logger.info(f"Received alert: {alert_data}")
        
        # Validate alert
        if not alert_data or 'ticker' not in alert_data:
            logger.warning("Invalid alert data received")
            return jsonify({"error": "Invalid alert data"}), 400
        
        # Apply filters
        filters = config['alert_filters']
        signal_count = int(alert_data.get('signals', 0))
        
        if signal_count < filters['min_signal_count']:
            logger.info(f"Alert filtered: signal count {signal_count} below minimum")
            return jsonify({"status": "filtered", "reason": "below_threshold"}), 200
        
        # Enrich alert with institutional data
        enriched_alert = enricher.enrich_alert(alert_data)
        logger.info(f"Alert enriched: {enriched_alert.get('ticker')}")
        
        # Send notifications
        notifier.notify(enriched_alert)
        
        # Forward to downstream systems
        forward_alert(enriched_alert)
        
        return jsonify({
            "status": "success",
            "ticker": enriched_alert.get('ticker'),
            "enriched": True
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling alert: {e}")
        return jsonify({"error": str(e)}), 500


def forward_alert(alert_data: Dict[str, Any]) -> None:
    """Forward enriched alert to downstream systems"""
    endpoints = config['webhook_endpoints']
    
    for name, endpoint_config in endpoints.items():
        try:
            response = requests.post(
                endpoint_config['url'],
                json=alert_data,
                headers=endpoint_config['headers'],
                timeout=endpoint_config['timeout'] / 1000
            )
            response.raise_for_status()
            logger.info(f"Alert forwarded to {name}")
            
        except Exception as e:
            logger.error(f"Error forwarding to {name}: {e}")
            
            # Retry logic
            for attempt in range(endpoint_config.get('retry_attempts', 0)):
                try:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    response = requests.post(
                        endpoint_config['url'],
                        json=alert_data,
                        headers=endpoint_config['headers'],
                        timeout=endpoint_config['timeout'] / 1000
                    )
                    response.raise_for_status()
                    logger.info(f"Alert forwarded to {name} on retry {attempt + 1}")
                    break
                except Exception as retry_error:
                    logger.error(f"Retry {attempt + 1} failed for {name}: {retry_error}")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
