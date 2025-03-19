from queue import PriorityQueue
import hashlib

class OTCManager:
    def __init__(self):
        self.buy_orders = PriorityQueue()
        self.sell_orders = PriorityQueue()
    
    def add_order(self, order_type: str, price: float, amount: float, token: str):
        order_id = hashlib.sha256(f"{price}{amount}{token}".encode()).hexdigest()
        if order_type == "buy":
            self.buy_orders.put((-price, order_id, {"amount": amount, "token": token}))
        else:
            self.sell_orders.put((price, order_id, {"amount": amount, "token": token}))
        self.match_orders()
    
    def match_orders(self):
        while not self.buy_orders.empty() and not self.sell_orders.empty():
            buy = self.buy_orders.queue[0]
            sell = self.sell_orders.queue[0]
            
            if -buy[0] >= sell[0]:  # Purchase price >= selling prices
                buy = self.buy_orders.get()
                sell = self.sell_orders.get()
                
                matched_amount = min(buy[2]["amount"], sell[2]["amount"])
                print(f"Matched {matched_amount} {buy[2]['token']} at ${sell[0]}")
                
                # Updating the remaining quantity
                if buy[2]["amount"] > matched_amount:
                    self.add_order("buy", -buy[0], buy[2]["amount"] - matched_amount, buy[2]["token"])
                if sell[2]["amount"] > matched_amount:
                    self.add_order("sell", sell[0], sell[2]["amount"] - matched_amount, sell[2]["token"])
            else:
                break
