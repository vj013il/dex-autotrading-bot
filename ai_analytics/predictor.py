import os
import logging
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Configuring logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Loading environment variables
load_dotenv()
DEXSCREENER_API_KEY = os.getenv("DEXSCREENER_API_KEY")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")  # To analyze the posts on X
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")  # To analyze Telegram channels

def fetch_market_data(token: str) -> Optional[Dict]:
    """
    Obtaining market data for a token with DEXscreener or Birdeye.
    
    Args:
        token (str): Token symbol (e.g., 'SOL' or contract address).
    
    Returns:
        Optional[Dict]: Token data (volume, liquidity, price) or None in case of error.
    """
    try:
        # Trying to get data from DEXscreener
        response = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{token}",
            headers={"Authorization": f"Bearer {DEXSCREENER_API_KEY}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Extracting key metrics
        market_data = {
            "volume_24h": data.get("volume", {}).get("h24", 0),
            "liquidity": data.get("liquidity", {}).get("usd", 0),
            "price_usd": data.get("price", {}).get("usd", 0),
            "price_change_24h": data.get("priceChange", {}).get("h24", 0)
        }
        logger.info(f"Fetched market data for {token}: {market_data}")
        return market_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching market data for {token}: {e}")
        return None

def analyze_social_signals(token: str, lookback_hours: int = 24) -> Dict:
    """
    Analyzing social signals from X and Telegram to estimate token popularity.
    
    Args:
        token (str): Символ токена.
        lookback_hours (int): Analysis period in hours (default 24).
    
    Returns:
        Dict: Social signal metrics (mentions, likelihood of pump).
    """
    try:
        # to analyze X
        x_response = requests.get(
            f"https://api.x.com/2/tweets/search/recent?query={token}",
            headers={"Authorization": f"Bearer {X_API_KEY}"},
            params={"max_results": 100, "since": (datetime.now() - timedelta(hours=lookback_hours)).isoformat()}
        )
        x_response.raise_for_status()
        x_data = x_response.json()
        x_mentions = len(x_data.get("data", []))

        # to analyze Telegram
        tg_response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/getUpdates",
            params={"timeout": 10}
        )
        tg_response.raise_for_status()
        tg_data = tg_response.json()
        tg_mentions = sum(1 for update in tg_data.get("result", []) if token.lower() in str(update).lower())

        # Calculating the probability of pump
        pump_probability = min(0.9, (x_mentions + tg_mentions) / 100.0)

        signals = {
            "x_mentions": x_mentions,
            "telegram_mentions": tg_mentions,
            "pump_probability": pump_probability,
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Social signals for {token}: {signals}")
        return signals
    except requests.exceptions.RequestException as e:
        logger.error(f"Error analyzing social signals for {token}: {e}")
        return {
            "x_mentions": 0,
            "telegram_mentions": 0,
            "pump_probability": 0.0,
            "last_updated": datetime.now().isoformat()
        }

def analyze_contract_safety(token_address: str) -> Dict:
