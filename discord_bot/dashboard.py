import discord
from news_data import get_daily_news_summary
from stock_data import analyze_stocks, format_stock_list

class DashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout None so it stays active

    @discord.ui.button(label="📰 Market News", style=discord.ButtonStyle.primary, custom_id="dashboard_news")
    async def btn_news(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        summary = get_daily_news_summary()
        # Discord has a 2000 character limit per message
        if len(summary) > 2000:
            summary = summary[:1997] + "..."
        await interaction.followup.send(summary, ephemeral=True) # Ephemeral so only the user sees it

    @discord.ui.button(label="📈 Trending Stocks", style=discord.ButtonStyle.success, custom_id="dashboard_trending")
    async def btn_trending(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Scanning for undervalued and growth stocks... this might take a moment.", ephemeral=True)
        results = analyze_stocks()
        msg = format_stock_list(results['undervalued'], 'Undervalued') + "\n" + format_stock_list(results['growth'], 'Growth')
        if len(msg) > 2000:
            msg = msg[:1997] + "..."
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="📱 Reddit Sentiment", style=discord.ButtonStyle.secondary, custom_id="dashboard_reddit")
    async def btn_reddit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fetching latest WSB sentiment... 🦍", ephemeral=True)
        from reddit_sentiment import get_reddit_sentiment
        sentiment = get_reddit_sentiment()
        await interaction.followup.send(sentiment, ephemeral=True)

    @discord.ui.button(label="🐋 Whale Options", style=discord.ButtonStyle.danger, custom_id="dashboard_whales")
    async def btn_whales(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Scanning near-term options chains for whale activity...", ephemeral=True)
        from options import scan_unusual_options
        flow = scan_unusual_options()
        await interaction.followup.send(flow, ephemeral=True)

    @discord.ui.button(label="📅 Upcoming Earnings", style=discord.ButtonStyle.secondary, custom_id="dashboard_earnings")
    async def btn_earnings(self, interaction: discord.Interaction, button: discord.ui.Button):
        # We will implement this in the next steps
        await interaction.response.send_message("Checking upcoming earnings calendar...", ephemeral=True)
        from earnings import get_upcoming_earnings
        earnings = get_upcoming_earnings()
        await interaction.followup.send(earnings, ephemeral=True)
