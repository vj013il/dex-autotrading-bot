 import requests
  import logging
  from src.config import (
      UNISWAP_V3_SUBGRAPH, SUSHISWAP_SUBGRAPH, AAVE_SUBGRAPH, CURVE_SUBGRAPH,
      BALANCER_SUBGRAPH, COMPOUND_SUBGRAPH, ARBITRUM_UNISWAP_SUBGRAPH
  )

  logger = logging.getLogger(__name__)

  def fetch_uniswap_pools():
      query = """
      {
        pools(first: 50, orderBy: volumeUSD, orderDirection: desc) {
          id
          token0 { symbol priceUSD }
          token1 { symbol priceUSD }
          feeTier
          volumeUSD
          totalValueLockedUSD
          poolDayData(first: 7, orderBy: date, orderDirection: desc) {
            date
            feesUSD
            volumeUSD
            open
            close
          }
          positions(first: 1000) { id liquidity }
        }
      }
      """
      try:
          response = requests.post(UNISWAP_V3_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['pools']
      except Exception as e:
          logger.error(f"Error fetching Uniswap V3 data: {e}")
          return []

  def fetch_sushiswap_pools():
      query = """
      {
        pairs(first: 50, orderBy: volumeUSD, orderDirection: desc) {
          id
          token0 { symbol priceUSD }
          token1 { symbol priceUSD }
          volumeUSD
          reserveUSD
          dayData(first: 7, orderBy: date, orderDirection: desc) {
            date
            volumeUSD
            feesUSD
          }
        }
      }
      """
      try:
          response = requests.post(SUSHISWAP_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['pairs']
      except Exception as e:
          logger.error(f"Error fetching SushiSwap data: {e}")
          return []

  def fetch_aave_markets():
      query = """
      {
        reserves(first: 50, orderBy: totalLiquidity, orderDirection: desc) {
          id
          symbol
          totalLiquidity
          liquidityRate
        }
      }
      """
      try:
          response = requests.post(AAVE_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['reserves']
      except Exception as e:
          logger.error(f"Error fetching Aave data: {e}")
          return []

  def fetch_curve_pools():
      query = """
      {
        pools(first: 50, orderBy: volumeUSD, orderDirection: desc) {
          id
          tokens { symbol priceUSD }
          volumeUSD
          totalValueLockedUSD
          dailyPoolSnapshots(first: 7, orderBy: timestamp, orderDirection: desc) {
            timestamp
            feesUSD
            volumeUSD
          }
        }
      }
      """
      try:
          response = requests.post(CURVE_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['pools']
      except Exception as e:
          logger.error(f"Error fetching Curve data: {e}")
          return []

  def fetch_balancer_pools():
      query = """
      {
        pools(first: 50, orderBy: totalLiquidity, orderDirection: desc) {
          id
          tokens { symbol priceUSD }
          totalLiquidity
          volumeUSD
          poolSnapshots(first: 7, orderBy: timestamp, orderDirection: desc) {
            timestamp
            feesUSD
            volumeUSD
          }
        }
      }
      """
      try:
          response = requests.post(BALANCER_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['pools']
      except Exception as e:
          logger.error(f"Error fetching Balancer data: {e}")
          return []

  def fetch_compound_markets():
      query = """
      {
        markets(first: 50, orderBy: totalSupply, orderDirection: desc) {
          id
          underlyingSymbol
          totalSupply
          supplyRate
        }
      }
      """
      try:
          response = requests.post(COMPOUND_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['markets']
      except Exception as e:
          logger.error(f"Error fetching Compound data: {e}")
          return []

  def fetch_arbitrum_pools():
      query = """
      {
        pools(first: 50, orderBy: volumeUSD, orderDirection: desc) {
          id
          token0 { symbol priceUSD }
          token1 { symbol priceUSD }
          feeTier
          volumeUSD
          totalValueLockedUSD
          poolDayData(first: 7, orderBy: date, orderDirection: desc) {
            date
            feesUSD
            volumeUSD
          }
        }
      }
      """
      try:
          response = requests.post(ARBITRUM_UNISWAP_SUBGRAPH, json={'query': query})
          response.raise_for_status()
          return response.json()['data']['pools']
      except Exception as e:
          logger.error(f"Error fetching Arbitrum data: {e}")
          return []

  def fetch_defi_safety_score(protocol_name):
      try:
          response = requests.get(f"https://api.defisafety.com/protocols?search={protocol_name}")
          response.raise_for_status()
          data = response.json()
          return data[0]['score'] if data else 0
      except Exception as e:
          logger.error(f"Error fetching DeFi Safety score for {protocol_name}: {e}")
          return 0
