from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per minute"])
