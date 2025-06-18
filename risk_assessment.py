  import numpy as np
  import logging
  from src.data_fetcher import fetch_defi_safety_score

  logger = logging.getLogger(__name__)

  def calculate_impermanent_loss(price_change):
      k = np.sqrt(abs(price_change))
      if k == 1 or price_change == 0:
          return 0
      il = (2 * k / (1 + k) - 1) * 100
      return abs(il)

  def assess_pool_risk(pool_data, protocol):
      try:
          safety_score = fetch_defi_safety_score(protocol)
          tvl = pool_data['tvl_usd']
          il = pool_data['il_percent']
          risk_score = (safety_score / 100) * (tvl / 1e6) / (il + 1)
          return {
              'safety_score': safety_score,
              'risk_score': risk_score,
              'risk_level': 'Low' if risk_score > 50 else 'Medium' if risk_score > 20 else 'High'
          }
      except Exception as e:
          logger.error(f"Error assessing risk for {protocol}: {e}")
          return {'safety_score': 0, 'risk_score': 0, 'risk_level': 'Unknown'}
