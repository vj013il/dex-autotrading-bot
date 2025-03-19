import hashlib

class ZKPVerifier:
    def __init__(self):
        self.secrets = {}
    
    def generate_proof(self, balance: float, secret: str) -> str:
        proof = hashlib.sha256(f"{balance}{secret}".encode()).hexdigest()
        self.secrets[proof] = balance
        return proof
    
    def verify_proof(self, proof: str, min_balance: float) -> bool:
        balance = self.secrets.get(proof, 0)
        return balance >= min_balance

# Utilization
zkp = ZKPVerifier()
secret = "user-secret-123"
proof = zkp.generate_proof(balance=15000, secret=secret)
is_valid = zkp.verify_proof(proof, 10000)  # True
