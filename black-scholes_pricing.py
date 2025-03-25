# Example: Options Pricing (Black-Scholes)
import math
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

# Example: Calculate a Call Option
S = 150  # Spot price
K = 160  # Strike price
T = 0.25 # Time to expiry (3 months)
r = 0.05 # Risk-free rate
sigma = 0.2 # Volatility

call_price = black_scholes(S, K, T, r, sigma, "call")
print(f"Call Option Price: ${call_price:.2f}")
