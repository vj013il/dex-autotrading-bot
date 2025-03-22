def gas_price_predictor(network: str) -> int:
    eth_gas = web3.eth.gas_price
    if network == "ethereum":
        return eth_gas * 1.2  # Add a buffer
    elif network == "arbitrum":
        return eth_gas * 0.1  # L2 cheaper
