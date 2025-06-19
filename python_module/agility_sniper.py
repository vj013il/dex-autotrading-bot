def snipe_new_dex(dex_address, web3):
    contract = web3.eth.contract(address=dex_address, abi=ABI)
    return contract.functions.isActive().call()
