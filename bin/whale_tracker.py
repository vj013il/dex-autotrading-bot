from web3 import Web3

def track_whales(pool_address: str):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    pool = w3.eth.contract(address=pool_address, abi=UNISWAP_ABI)
    event_filter = pool.events.Swap.createFilter(fromBlock='latest')
    while True:
        for event in event_filter.get_new_entries():
            if event['args']['amount'] > 1e6:  # Deal > $1M
                alert_whale_activity(event)
