from discord_bot.charts import generate_chart
res = generate_chart('AAPL')
print("Result AAPL:", res)

res_invalid = generate_chart('INVALID_TICKER123')
print("Result Invalid:", res_invalid)
