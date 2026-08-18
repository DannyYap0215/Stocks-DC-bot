import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

# Import our custom modules
from stock_data import analyze_stocks, format_stock_list
from news_data import check_for_major_news, get_daily_news_summary, format_major_news
from portfolio import add_to_portfolio, view_portfolio

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID') # Optional: ID of the channel to post automated updates

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    # Try to send a startup message to the configured channel
    channel = None
    if CHANNEL_ID:
        try:
            channel = bot.get_channel(int(CHANNEL_ID))
        except ValueError:
            pass

    if not channel:
        for guild in bot.guilds:
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    channel = c
                    break
            if channel:
                break

    if channel:
        try:
            await channel.send(f"✅ **{bot.user.name}** is online and ready! Try typing `!news` or `!undervalued`.")
        except discord.errors.Forbidden:
            print(f"ERROR: Bot does not have permission to send messages in channel {channel.name}.")

    # Start background tasks
    if not major_news_scanner.is_running():
        major_news_scanner.start()

    if not daily_summary.is_running():
        daily_summary.start()

# --- Commands ---

@bot.group(name='portfolio', invoke_without_command=True, help='Manage your personal portfolio. Type !portfolio for commands.')
async def portfolio_group(ctx):
    """Portfolio management root command."""
    if ctx.invoked_subcommand is None:
        await ctx.send("Available commands:\n`!portfolio add <ticker> <shares> <price>`\n`!portfolio view`")

@portfolio_group.command(name='add', help='Add a stock to your portfolio: !portfolio add NVDA 10 125.50')
async def portfolio_add(ctx, ticker: str, shares: float, price: float):
    user_id = ctx.author.id
    try:
        add_to_portfolio(user_id, ticker, shares, price)
        await ctx.send(f"✅ Added {shares} shares of {ticker.upper()} at ${price:.2f} to your portfolio.")
    except Exception as e:
        await ctx.send(f"❌ Error adding to portfolio: {e}")

@portfolio_group.command(name='view', help='View your current portfolio')
async def portfolio_view(ctx):
    await ctx.send("Fetching your portfolio data...")
    user_id = ctx.author.id
    try:
        result = view_portfolio(user_id)
        await ctx.send(result)
    except Exception as e:
        await ctx.send(f"❌ Error fetching portfolio: {e}")


@bot.command(name='undervalued', help='Shows top undervalued stocks based on P/E ratio')
async def show_undervalued(ctx):
    await ctx.send("Scanning for undervalued stocks... This might take a moment.")
    results = analyze_stocks()
    formatted = format_stock_list(results['undervalued'], 'Undervalued')
    await ctx.send(formatted)

@bot.command(name='growth', help='Shows stocks with steady recent growth')
async def show_growth(ctx):
    await ctx.send("Scanning for growth stocks... This might take a moment.")
    results = analyze_stocks()
    formatted = format_stock_list(results['growth'], 'Growth')
    await ctx.send(formatted)

@bot.command(name='fomo', help='Shows overhyped stocks to potentially avoid')
async def show_fomo(ctx):
    await ctx.send("Scanning for FOMO stocks... This might take a moment.")
    results = analyze_stocks()
    formatted = format_stock_list(results['fomo'], 'FOMO')
    await ctx.send(formatted)

@bot.command(name='news', help='Shows a summary of the latest financial news')
async def show_news(ctx):
    await ctx.send("Fetching latest news...")
    summary = get_daily_news_summary()

    # Discord has a 2000 character limit per message, ensure we don't exceed it
    if len(summary) > 2000:
        summary = summary[:1997] + "..."

    await ctx.send(summary)

# --- Background Tasks ---

@tasks.loop(minutes=5)
async def major_news_scanner():
    """Scans for major news every 5 minutes and posts if found."""
    # We need a channel to post to. We can use a configured channel ID from .env
    # or just post to the first text channel the bot has access to (less reliable)
    channel = None
    if CHANNEL_ID:
        try:
            channel = bot.get_channel(int(CHANNEL_ID))
        except ValueError:
            pass

    if not channel:
        # Fallback: try to find a channel named 'general' or similar
        for guild in bot.guilds:
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    channel = c
                    break
            if channel:
                break

    if not channel:
        return # No place to send messages

    alerts = check_for_major_news()
    if alerts:
        alert_msg = format_major_news(alerts)
        if alert_msg:
            # Handle max discord msg length
            if len(alert_msg) > 2000:
                alert_msg = alert_msg[:1997] + "..."
            await channel.send(alert_msg)

@tasks.loop(hours=24)
async def daily_summary():
    """Posts a daily summary of stocks and news."""
    channel = None
    if CHANNEL_ID:
        try:
            channel = bot.get_channel(int(CHANNEL_ID))
        except ValueError:
            pass

    if not channel:
        for guild in bot.guilds:
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    channel = c
                    break
            if channel:
                break

    if not channel:
        return

    await channel.send("📊 **Daily Market Summary** 📊")

    # Send News
    news = get_daily_news_summary()
    await channel.send(news[:2000])

    # Send Stocks
    await channel.send("Scanning today's stock metrics...")
    results = analyze_stocks()

    await channel.send(format_stock_list(results['undervalued'], 'Undervalued'))
    await channel.send(format_stock_list(results['growth'], 'Growth'))
    await channel.send(format_stock_list(results['fomo'], 'FOMO (Overhyped)'))

if __name__ == "__main__":
    if TOKEN:
        print("Starting bot...")
        bot.run(TOKEN)
    else:
        print("ERROR: DISCORD_TOKEN not found. Please set it in your .env file.")
