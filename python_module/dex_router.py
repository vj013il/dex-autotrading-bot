def route_dex_trade(dex_list, token_pair):
    return min(dex_list, key=lambda x: x['latency'])
