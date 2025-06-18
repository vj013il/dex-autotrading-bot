     import dash
     from dash import dcc, html, dash_table
     from dash.dependencies import Input, Output
     import logging
     from src.data_fetcher import fetch_uniswap_pools, fetch_sushiswap_pools, fetch_aave_markets, fetch_curve_pools, fetch_balancer_pools, fetch_compound_markets, fetch_arbitrum_pools
     from src.analytics import generate_recommendations
     from src.visualization import create_visualizations
     from src.notifications import send_telegram_notification

     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
     logger = logging.getLogger(__name__)

     app = dash.Dash(__name__ )

     app.layout = html.Div([
         html.H1("DeFi Analytics Dashboard"),
         dcc.Interval(id='interval-component', interval=3600*1000, n_intervals=0),
         dash_table.DataTable(id='table', style_table={'overflowX': 'auto'}),
         dcc.Graph(id='scatter-plot'),
     ])

     @app.callback(
         [Output('table', 'data'), Output('table', 'columns'), Output('scatter-plot', 'figure')],
         Input('interval-component', 'n_intervals')
     )
     def update_dashboard(n):
         df = generate_recommendations()
         if df is None:
             logger.warning("No data available")
             return [], [], {}
         columns = [{'name': col, 'id': col} for col in df.columns]
         data = df.to_dict('records')
         fig = create_visualizations(df)

         # Telegram notification for top 3
         top_pools = df.head(3)
         message = "Top-3 DeFi Opportunities:\n"
         for _, row in top_pools.iterrows():
             message += (f"{row['protocol']}: {row['pair']} | APY {row['apy_percent']:.2f}% | "
                         f"IL {row['il_percent']:.2f}% | TVL ${row['tvl_usd']:,.0f}\n")
         import asyncio
         asyncio.run(send_telegram_notification(message))

         return data, columns, fig

     if __name__ == "__main__":
         logger.info("Starting DeFi Analytics Bot")
         app.run_server(debug=False, host='0.0.0.0', port=8050)
     ```
