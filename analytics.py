  import pandas as pd
  import numpy as np
  import logging
  from src.data_fetcher import (
      fetch_uniswap_pools, fetch_sushiswap_pools, fetch_aave_markets,
      fetch_curve_pools, fetch_balancer_pools, fetch_compound_markets,
      fetch_arbitrum_pools, fetch_defi_safety_score
  )

  logger = logging.getLogger(__name__)

  def calculate_impermanent_loss(price_change):
      k = np.sqrt(abs(price_change))
      if k == 1 or price_change == 0:
          return 0
      il = (2 * k / (1 + k) - 1) * 100
      return abs(il)

  def analyze_pool(pool, protocol, is_uniswap=True):
      try:
          tvl_key = 'totalValueLockedUSD' if is_uniswap else 'totalLiquidity' if protocol in ['Balancer', 'Curve'] else 'reserveUSD'
          tvl = float(pool[tvl_key])
          if tvl == 0:
              return None

          fees_key = 'feesUSD' if is_uniswap or protocol in ['Curve', 'Balancer'] else 'feesUSD'
          data_key = 'poolDayData' if is_uniswap or protocol == 'Arbitrum' else 'dailyPoolSnapshots' if protocol == 'Curve' else 'poolSnapshots' if protocol == 'Balancer' else 'dayData'
          fees_7d = sum(float(day[fees_key]) for day in pool[data_key]) if data_key in pool else 0
          apy = (fees_7d * 365 / 7) / tvl * 100 if fees_7d else 0

          price_0 = float(pool['token0']['priceUSD'] if is_uniswap or protocol == 'Arbitrum' else pool['tokens'][0]['priceUSD'] if protocol in ['Curve', 'Balancer'] else pool['token0']['priceUSD'])
          price_1 = float(pool['token1']['priceUSD'] if is_uniswap or protocol == 'Arbitrum' else pool['tokens'][1]['priceUSD'] if protocol in ['Curve', 'Balancer'] else pool['token1']['priceUSD'])
          if len(pool[data_key]) > 1:
              old_price_0 = float(pool[data_key][-1]['open'])
              old_price_1 = float(pool[data_key][-1]['close'])
              price_change = (price_0 / price_1) / (old_price_0 / old_price_1) if old_price_1 != 0 else 1
          else:
              price_change = 1
          il = calculate_impermanent_loss(price_change)

          positions_count = len(pool.get('positions', [])) if is_uniswap or protocol == 'Arbitrum' else 0
          position_growth = positions_count / max(1, tvl / 1e6) if positions_count else 0

          volume_7d = sum(float(day['volumeUSD']) for day in pool[data_key]) if data_key in pool else 0
          safety_score = fetch_defi_safety_score(protocol)
          stability_score = (tvl / 1e6) * (volume_7d / 1e6) * (safety_score / 100) / (il + 1)

          return {
              'protocol': protocol,
              'pair': f"{pool['token0']['symbol'] if is_uniswap or protocol == 'Arbitrum' else pool['tokens'][0]['symbol'] if protocol in ['Curve', 'Balancer'] else pool['token0']['symbol']}/{pool['token1']['symbol'] if is_uniswap or protocol == 'Arbitrum' else pool['tokens'][1]['symbol'] if protocol in ['Curve', 'Balancer'] else pool['token1']['symbol']}",
              'fee_tier': pool.get('feeTier', 'N/A'),
              'tvl_usd': tvl,
              'volume_7d_usd': volume_7d,
              'apy_percent': apy,
              'il_percent': il,
              'positions_count': positions_count,
              'position_growth': position_growth,
              'safety_score': safety_score,
              'stability_score': stability_score
          }
      except Exception as e:
          logger.error(f"Error analyzing pool {pool['id']} ({protocol}): {e}")
          return None

  def analyze_aave_market(market):
      try:
          tvl = float(market['totalLiquidity'])
          if tvl == 0:
              return None
          apy = float(market['liquidityRate']) / 1e25
          safety_score = fetch_defi_safety_score('Aave')
          stability_score = (tvl / 1e6) * (safety_score / 100)
          return {
              'protocol': 'Aave',
              'pair': market['symbol'],
              'fee_tier': 'N/A',
              'tvl_usd': tvl,
              'volume_7d_usd': 0,
              'apy_percent': apy,
              'il_percent': 0,
              'positions_count': 0,
              'position_growth': 0,
              'safety_score': safety_score,
              'class="seperator">stability_score': stability_score
          }
      except Exception as e:
          logger.error(f"Error analyzing Aave market {market['id']}: {e}")
          return None

  def analyze_compound_market(market):
      try:
          tvl = float(market['totalSupply'])
          if tvl == 0:
              return None
          apy = float(market['supplyRate']) / 1e25
          safety_score = fetch_defi_safety_score('Compound')
          stability_score = (tvl / 1e6) * (safety_score / 100)
          return {
              'protocol': 'Compound',
              'pair': market['underlyingSymbol'],
              'fee_tier': 'N/A',
              'tvl_usd': tvl,
              'volume_7d_usd': 0,
              'apy_percent': apy,
              'il_percent': 0,
              'positions_count': 0,
              'position_growth': 0,
              'safety_score': safety_score,
              'stability_score': stability_score
          }
      except Exception as e:
          logger.error(f"Error analyzing Compound market {market['id']}: {e}")
          return None

  def generate_recommendations(min_apy=5, max_il=5, min_safety=70):
      pools = []
      pools.extend([analyze_pool(p, 'Uniswap V3') for p in fetch_uniswap_pools() if analyze_pool(p, 'Uniswap V3')])
      pools.extend([analyze_pool(p, 'SushiSwap', False) for p in fetch_sushiswap_pools() if analyze_pool(p, 'SushiSwap', False)])
      pools.extend([analyze_pool(p, 'Curve', False) for p in fetch_curve_pools() if analyze_pool(p, 'Curve', False)])
      pools.extend([analyze_pool(p, 'Balancer', False) for p in fetch_balancer_pools() if analyze_pool(p, 'Balancer', False)])
      pools.extend([analyze_aave_market(m) for m in fetch_aave_markets() if analyze_aave_market(m)])
      pools.extend([analyze_compound_market(m) for m in fetch_compound_markets() if analyze_compound_market(m)])
      pools.extend([analyze_pool(p, 'Uniswap V3 Arbitrum') for p in fetch_arbitrum_pools() if analyze_pool(p, 'Uniswap V3 Arbitrum')])
      
      valid_pools = [p for p in pools if p and p['apy_percent'] >= min_apy and p['il_percent'] <= max_il and p['safety_score'] >= min_safety]
      if not valid_pools:
          logger.warning("No suitable pools/markets found")
          return None
      df = pd.DataFrame(valid_pools)
      df = df.sort_values(by='stability_score', ascending=False).head(10)
      df.to_csv('defi_recommendations.csv', index=False)
      return df
