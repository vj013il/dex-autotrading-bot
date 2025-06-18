  import logging

  logger = logging.getLogger(__name__)

  def safe_float(value):
      try:
          return float(value)
      except (ValueError, TypeError):
          logger.warning(f"Invalid float conversion: {value}")
          return 0.0
