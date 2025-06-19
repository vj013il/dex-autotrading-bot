import asyncio
import logging
from web3 import Web3
from strategy_config import load_strategy
from presale_monitor import monitor_presale
from dex_router import route_dex_trade
from arbitrage_scanner import scan_arbitrage
from stop_loss import apply_stop_loss
from take_profit import apply_take_profit
from config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_bot(config):
    """Initialize bot components and connections."""
    try:
        # Connect to Web3 provider
        web3 = Web3(Web3.WebsocketProvider(config['network']['rpc_endpoint']))
        if not web3.is_connected():
            raise ConnectionError("Failed to connect to Web3 provider")
        
        logger.info(f"Connected to {config['network']['name']} via {config['network']['rpc_endpoint']}")
        
        # Load wallet (private key stored securely in config)
        account = web3.eth.account.from_key(config['wallet']['private_key'])
        
        return web3, account
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        raise

async def run_sniper(config, web3):
    """Run mempool and presale sniping logic."""
    strategy = load_strategy(config['strategy']['file'])
    dex_list = config['dexs']
    
    while True:
        try:
            # Scan mempool for new token pairs
            token_pairs = [(pair['token0'], pair['token1']) for pair in strategy['pairs']]
            for pair in token_pairs:
                dex = route_dex_trade(dex_list, pair)
                logger.info(f"Sniping pair {pair} on {dex['name']}")
                # Call Rust transaction processor (placeholder for FFI integration)
                # await process_transaction(account, tx_request)
            
            # Monitor presales
            for presale in config['presales']:
                vesting = monitor_presale(presale['contract'], web3)
                if vesting['is_active']:
                    logger.info(f"Presale active at {presale['contract']}")
                    # Trigger presale snipe (Rust integration)
            
            await asyncio.sleep(0.1)  # Control polling rate
        except Exception as e:
            logger.error(f"Sniper error: {str(e)}")
            await asyncio.sleep(1)

async def run_trading(config, web3, account):
    """Run trading strategies like arbitrage, stop-loss, and take-profit."""
    while True:
        try:
            # Scan for arbitrage opportunities
            prices = [{'dex': dex['name'], 'price': 100} for dex in config['dexs']]  # Placeholder
            opportunities = scan_arbitrage(prices)
            for opp in opportunities:
                logger.info(f"Arbitrage opportunity: {opp[0]['dex']} -> {opp[1]['dex']}")
                # Execute arbitrage trade (Rust integration)
            
            # Apply stop-loss and take-profit
            for position in config['portfolio']:
                current_price = 95  # Placeholder
                if apply_stop_loss(current_price, position['entry_price']):
                    logger.info(f"Stop-loss triggered for {position['token']}")
                    # Sell position (Rust integration)
                if apply_take_profit(current_price, position['entry_price']):
                    logger.info(f"Take-profit triggered for {position['token']}")
                    # Sell position (Rust integration)
            
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Trading error: {str(e)}")
            await asyncio.sleep(1)

async def main():
    """Main entry point for HyperSnipeX bot."""
    config = load_config('config.json')
    web3, account = await initialize_bot(config)
    
    # Start sniper and trading tasks concurrently
    await asyncio.gather(
        run_sniper(config, web3),
        run_trading(config, web3, account)
    )

if __name__ == "__main__":
    asyncio.run(main())
