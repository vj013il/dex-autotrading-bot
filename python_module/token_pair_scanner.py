def scan_token_pairs(dex):
    return [(pair['token0'], pair['token1']) for pair in dex.pairs]
