async def fetch_prices(client, dex_list, dark_pools, token_pair):
    prices = {}
    for platform in dex_list + dark_pools:
        prices[platform] = await get_platform_price(client, platform, token_pair)
    return prices

async def get_platform_price(client, platform, token_pair):
    import random 
    return random.uniform(90, 110)
