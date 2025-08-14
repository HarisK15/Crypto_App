import requests
import json
import streamlit as st
import time
import logging
from typing import Dict, Optional, List
from requests.exceptions import RequestException, Timeout

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API settings
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 1.1  # Slightly over 1 second to respect rate limits

@st.cache_data(ttl=300)  # Cache for 5 minutes instead of 50 minutes
def fetch_price(coin_id: str) -> Optional[float]:
    """
    Gets the current price for a single coin from CoinGecko.
    
    Args:
        coin_id: The coin identifier (e.g., 'bitcoin', 'ethereum')
        
    Returns:
        Price in USD or None if something goes wrong
    """
    if not coin_id or not isinstance(coin_id, str):
        logger.error(f"Invalid coin_id: {coin_id}")
        return None
        
    url = f"{COINGECKO_BASE_URL}/simple/price?ids={coin_id}&vs_currencies=usd"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if coin_id not in data:
            logger.warning(f"Coin {coin_id} not found in API response")
            return None
            
        price = data[coin_id].get("usd")
        if price is None:
            logger.warning(f"No USD price found for {coin_id}")
            return None
            
        # Wait a bit to respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
        return price
        
    except RequestException as e:
        logger.error(f"Request failed for {coin_id}: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error for {coin_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {coin_id}: {e}")
        return None

def fetch_watchlist(watchlist_file: str) -> List[Dict]:
    """
    Loads the watchlist from a JSON file.
    
    Args:
        watchlist_file: Path to the watchlist JSON file
        
    Returns:
        List of watchlist items or empty list if something goes wrong
    """
    try:
        with open(watchlist_file, 'r') as f:
            watchlist = json.load(f)
            return watchlist if isinstance(watchlist, list) else []
    except FileNotFoundError:
        logger.warning(f"Watchlist file {watchlist_file} not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in watchlist file: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading watchlist: {e}")
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_prices_batch(coin_list: List[str]) -> Dict[str, Dict]:
    """
    Gets prices for multiple coins in one API call.
    
    Args:
        coin_list: List of coin identifiers
        
    Returns:
        Dictionary mapping coin_id to price data
    """
    if not coin_list:
        logger.warning("Empty coin list provided")
        return {}
        
    # Filter out invalid coin IDs
    valid_coins = [coin for coin in coin_list if coin and isinstance(coin, str)]
    if not valid_coins:
        logger.error("No valid coin IDs provided")
        return {}
        
    ids_string = ",".join(valid_coins)
    url = f"{COINGECKO_BASE_URL}/simple/price?ids={ids_string}&vs_currencies=usd"
    
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Make sure the response looks right
        if not isinstance(data, dict):
            logger.error("Invalid API response format")
            return {}
            
        # Wait a bit to respect rate limits
        time.sleep(RATE_LIMIT_DELAY)
        return data
        
    except RequestException as e:
        logger.error(f"Batch price fetch failed: {e}")
        return {}
    except (KeyError, ValueError) as e:
        logger.error(f"Data parsing error in batch fetch: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error in batch fetch: {e}")
        return {}

def validate_coin_id(coin_id: str) -> bool:
    """
    Checks if a coin ID looks valid.
    
    Args:
        coin_id: The coin identifier to check
        
    Returns:
        True if it looks valid, False otherwise
    """
    if not coin_id or not isinstance(coin_id, str):
        return False
    # Basic check - coin IDs should be lowercase, alphanumeric with hyphens
    return coin_id.replace('-', '').replace('_', '').isalnum() and coin_id.islower()
