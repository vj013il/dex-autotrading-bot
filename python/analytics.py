import logging
import sqlite3
import json
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Analytics:
    def __init__(self, db_path: str = "trades.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                buy_platform TEXT,
                sell_platform TEXT,
                pair TEXT,
                buy_price REAL,
                sell_price REAL,
                volume REAL,
                profit REAL
            )
        ''')
        self.conn.commit()

    def log_trade(self, opportunity: Dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (timestamp, buy_platform, sell_platform, pair, buy_price, sell_price, volume, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            opportunity['buy_platform'],
            opportunity['sell_platform'],
            opportunity['pair'],
            opportunity['buy_price'],
            opportunity['sell_price'],
            opportunity['volume'],
            opportunity['profit']
        ))
        self.conn.commit()

    def get_metrics(self) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(profit), AVG(profit) FROM trades')
        count, total_profit, avg_profit = cursor.fetchone()
        return {
            'total_trades': count or 0,
            'total_profit': total_profit or 0.0,
            'average_profit': avg_profit or 0.0
        }

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    analytics = Analytics()
    # Example usage
    opportunity = {
        'buy_platform': 'binance',
        'sell_platform': 'kucoin',
        'pair': 'SOL/USDT',
        'buy_price': 150.3,
        'sell_price': 150.5,
        'volume': 10000.0,
        'profit': 2000.0
    }
    analytics.log_trade(opportunity)
    print(analytics.get_metrics())
