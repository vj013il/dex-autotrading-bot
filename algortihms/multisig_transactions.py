class MultisigWallet:
    def __init__(self, owners: list, threshold: int):
        self.owners = owners
        self.threshold = threshold
        self.pending_txs = {}
    
    def propose_transaction(self, tx_data: dict) -> str:
        tx_id = hashlib.sha256(str(tx_data).encode()).hexdigest()
        self.pending_txs[tx_id] = {
            "data": tx_data,
            "approvals": set(),
            "executed": False
        }
        return tx_id
    
    def approve_transaction(self, tx_id: str, signer: str) -> bool:
        if tx_id not in self.pending_txs:
            return False
        
        if signer not in self.owners:
            return False
        
        self.pending_txs[tx_id]["approvals"].add(signer)
        
        if len(self.pending_txs[tx_id]["approvals"]) >= self.threshold:
            self.execute_transaction(tx_id)
            return True
        return False
    
    def execute_transaction(self, tx_id: str):
        # Here is the integration with Solana RPC
        print(f"Executing TX {tx_id}: {self.pending_txs[tx_id]['data']}")
        self.pending_txs[tx_id]["executed"] = True
