import discord
from news_data import get_daily_news_summary
from stock_data import analyze_stocks, format_stock_list

class ChartModal(discord.ui.Modal, title='View Stock Chart'):
    ticker = discord.ui.TextInput(
        label='Ticker Symbol',
        placeholder='e.g., AAPL, NVDA, TSLA',
        required=True,
        max_length=10,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ticker_val = self.ticker.value.upper().strip()

        import asyncio
        from charts import generate_chart

        # Run blocking generation in an executor thread
        loop = asyncio.get_event_loop()
        chart_file = await loop.run_in_executor(None, generate_chart, ticker_val)

        if chart_file == "RATE_LIMITED":
            await interaction.followup.send(f"⚠️ Yahoo Finance rate limit exceeded. Please try again later.", ephemeral=True)
        elif chart_file:
            await interaction.followup.send(f"📊 Chart for **{ticker_val}**:", file=chart_file, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Could not generate chart for **{ticker_val}**. Invalid ticker or no data.", ephemeral=True)

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout None so it stays active

    @discord.ui.button(label="📰 Market News", style=discord.ButtonStyle.primary, custom_id="dashboard_news")
    async def btn_news(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        import asyncio
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(None, get_daily_news_summary)

        # Discord has a 2000 character limit per message
        if len(summary) > 2000:
            summary = summary[:1997] + "..."
        await interaction.followup.send(summary, ephemeral=True)

    @discord.ui.button(label="📈 Trending Stocks", style=discord.ButtonStyle.success, custom_id="dashboard_trending")
    async def btn_trending(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        import asyncio
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, analyze_stocks)

        msg = format_stock_list(results['undervalued'], 'Undervalued') + "\n" + format_stock_list(results['growth'], 'Growth')
        if len(msg) > 2000:
            msg = msg[:1997] + "..."
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="📱 Reddit Sentiment", style=discord.ButtonStyle.secondary, custom_id="dashboard_reddit")
    async def btn_reddit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        import asyncio
        from reddit_sentiment import get_reddit_sentiment
        loop = asyncio.get_event_loop()
        sentiment = await loop.run_in_executor(None, get_reddit_sentiment)
        await interaction.followup.send(sentiment, ephemeral=True)

    @discord.ui.button(label="🐋 Whale Options", style=discord.ButtonStyle.danger, custom_id="dashboard_whales")
    async def btn_whales(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        import asyncio
        from options import scan_unusual_options
        loop = asyncio.get_event_loop()
        flow = await loop.run_in_executor(None, scan_unusual_options)
        await interaction.followup.send(flow, ephemeral=True)

    @discord.ui.button(label="📅 Upcoming Earnings", style=discord.ButtonStyle.secondary, custom_id="dashboard_earnings")
    async def btn_earnings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        import asyncio
        from earnings import get_upcoming_earnings
        loop = asyncio.get_event_loop()
        earnings = await loop.run_in_executor(None, get_upcoming_earnings)
        await interaction.followup.send(earnings, ephemeral=True)

    @discord.ui.button(label="📊 View Chart", style=discord.ButtonStyle.primary, custom_id="dashboard_chart", row=1)
    async def btn_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        # We must return the Modal instantly, we cannot defer first for Modals
        await interaction.response.send_modal(ChartModal())
