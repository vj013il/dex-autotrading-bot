def plot_heatmap(order_book: dict):
    import matplotlib.pyplot as plt
    bids = order_book['bids']
    asks = order_book['asks']
    plt.figure(figsize=(10, 6))
    plt.scatter([b[0] for b in bids], [b[1] for b in bids], c='green', label='Bids')
    plt.scatter([a[0] for a in asks], [a[1] for a in asks], c='red', label='Asks')
    plt.title("Liquidity Heatmap")
    plt.xlabel("Price")
    plt.ylabel("Volume")
    plt.legend()
    plt.show()
