def generate_trade_alert(signal):
    """Auto-post to Twitter/Discord"""
    message = f"🚨 ALERT: {signal.coin} {signal.action} @ ${signal.price}"
    post_to_twitter(message)
    post_to_discord(message, channel='trading-alerts')
