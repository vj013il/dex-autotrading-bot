def generate_dashboard():
    df = pd.DataFrame({
        'Pool': ['Uniswap', 'Curve', 'Balancer'],
        'APR': [get_apr('uniswap'), get_apr('curve'), get_apr('balancer')]
    })
    df.plot(kind='bar', x='Pool', y='APR')
