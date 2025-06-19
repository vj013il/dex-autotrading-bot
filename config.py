import json
import os
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(file_path: str) -> Dict[str, Any]:
    """Load and validate configuration from a JSON file."""
    if not os.path.exists(file_path):
        logger.error(f"Config file {file_path} not found, creating default config")
        create_default_config(file_path)
    
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        # Validate config
        required_keys = ['network', 'wallet', 'dexs', 'strategy', 'presales']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required config key: {key}")
        
        logger.info(f"Configuration loaded from {file_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {str(e)}")
        raise

def create_default_config(file_path: str) -> None:
    """Create a default configuration file if none exists."""
    default_config = {
        "network": {
            "name": "Ethereum",
            "rpc_endpoint": "wss://mainnet.infura.io/v3/YOUR_INFURA_KEY",
            "chain_id": 1
        },
        "wallet": {
            "private_key": "YOUR_PRIVATE_KEY",
            "address": "0xYOUR_ADDRESS"
        },
        "dexs": [
            {"name": "Uniswap", "address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", "latency": 10},
            {"name": "PancakeSwap", "address": "0x10ED43C718714eb63d5aA57B78B54704E256024E", "latency": 12}
        ],
        "strategy": {
            "file": "strategy.json",
            "parameters": {
                "stop_loss_threshold": 0.05,
                "take_profit_threshold": 0.1,
                "buy_dip_trigger": 0.95
            }
        },
        "presales": [
            {"platform": "Pinksale", "contract": "0xCONTRACT_ADDRESS", "vesting_check": True}
        ],
        "security": {
            "honeypot_scan": True,
            "rug_pull_monitor": True,
            "anti_bot_delay": 100
        },
        "portfolio": [
            {"token": "TOKEN_ADDRESS", "entry_price": 100}
        ]
    }
    
    try:
        with open(file_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        logger.info(f"Default config created at {file_path}")
    except Exception as e:
        logger.error(f"Failed to create default config: {str(e)}")
        raise

def update_config(file_path: str, key: str, value: Any) -> None:
    """Update a specific configuration parameter and save to file."""
    config = load_config(file_path)
    config[key] = value
    
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Config updated: {key} = {value}")
    except Exception as e:
        logger.error(f"Failed to update config: {str(e)}")
        raise
