def check_liquidity(contract, web3):
    return web3.eth.get_balance(contract.address)
