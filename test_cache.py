from discord_bot.stock_data import get_live_price, get_stock_metrics
import time

print("First call to get_live_price:")
start = time.time()
print(get_live_price('AAPL'))
print(f"Time: {time.time() - start:.2f}s")

print("\nSecond call to get_live_price (should be cached):")
start = time.time()
print(get_live_price('AAPL'))
print(f"Time: {time.time() - start:.2f}s")
