import schedule

class AutoRebalancer:
    def __init__(self, interval_minutes: int):
        self.interval = interval_minutes
        self.is_active = False

    def start(self):
        """Starting periodic rebalancing"""
        self.is_active = True
        schedule.every(self.interval).minutes.do(self.rebalance)
        
        while self.is_active:
            schedule.run_pending()
            time.sleep(1)

    def rebalance(self):
        """Order repositioning logic"""
        print(f"Rebalancing at {time.ctime()}")
        # 1. Cancel old warrants
        # 2. Calculate new prices
        # 3. Place new orders

    def stop(self):
        self.is_active = False
