from web3 import Web3

def monitor_presale(contract_address, web3):
    contract = web3.eth.contract(address=contract_address, abi=ABI)
    return contract.functions.vestingPeriod().call()
