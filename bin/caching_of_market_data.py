import redis

r = redis.Redis()

def cache_orderbook(exchange: str, symbol: str, data: dict):
    key = f"{exchange}:{symbol}:orderbook"
    r.setex(key, 100, json.dumps(data))  # TTL 100 ms

def get_cached_orderbook(exchange: str, symbol: str):
    return json.loads(r.get(f"{exchange}:{symbol}:orderbook"))
