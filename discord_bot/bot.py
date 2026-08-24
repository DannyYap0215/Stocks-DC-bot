import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv

# Import our custom modules
from stock_data import analyze_stocks, format_stock_list, get_live_price, scan_unusual_activity
from news_data import check_for_major_news, get_daily_news_summary, format_major_news
from portfolio import add_to_portfolio, view_portfolio
from alerts import add_alert, get_user_alerts, remove_alert, get_all_alerts, remove_alert_by_value
from dashboard import DashboardView
from charts import generate_chart

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

    # Register the persistent view so buttons work after restarts
    bot.add_view(DashboardView())

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
            view = DashboardView()
            embed = discord.Embed(
                title="📊 Ultimate Trading Dashboard",
                description="Click the buttons below to instantly access live market intel, social sentiment, and alerts without typing commands.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Powered by the Ultimate Trading Bot | Type !dashboard to see this again")
            await channel.send(f"✅ **{bot.user.name}** is online and ready!", embed=embed, view=view)
        except discord.errors.Forbidden:
            print(f"ERROR: Bot does not have permission to send messages in channel {channel.name}.")

    # Start background tasks
    if not major_news_scanner.is_running():
        major_news_scanner.start()

    if not daily_summary.is_running():
        daily_summary.start()

    if not check_price_alerts.is_running():
        check_price_alerts.start()

    if not unusual_activity_scanner.is_running():
        unusual_activity_scanner.start()

# --- Commands ---

@bot.command(name='dashboard', aliases=['menu', 'hub'], help='Opens the interactive trading dashboard')
async def show_dashboard(ctx):
    view = DashboardView()
    embed = discord.Embed(
        title="📊 Ultimate Trading Dashboard",
        description="Click the buttons below to instantly access live market intel, social sentiment, and alerts without typing commands.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Powered by the Ultimate Trading Bot")
    await ctx.send(embed=embed, view=view)

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

# --- Alert Commands ---

@bot.group(name='alert', invoke_without_command=True, help='Manage custom price alerts. Type !alert for commands.')
async def alert_group(ctx):
    """Alert management root command."""
    if ctx.invoked_subcommand is None:
        await ctx.send("Available commands:\n`!alert add <ticker> < > or < > <price>` (e.g. `!alert add AAPL > 150`)\n`!alert list`\n`!alert remove <id>`")

@alert_group.command(name='add', help='Add a price alert: !alert add AAPL > 150')
async def alert_add(ctx, ticker: str, condition: str, price: float):
    if condition not in ['>', '<']:
        await ctx.send("❌ Condition must be either `>` or `<`. Example: `!alert add AAPL > 150`")
        return

    user_id = ctx.author.id
    try:
        added = add_alert(user_id, ticker, condition, price)
        if added:
            await ctx.send(f"✅ Alert set: I will DM you when **{ticker.upper()}** is **{condition} ${price:.2f}**.")
        else:
            await ctx.send(f"⚠️ You already have an exact alert set for **{ticker.upper()} {condition} ${price:.2f}**.")
    except Exception as e:
        await ctx.send(f"❌ Error adding alert: {e}")

@alert_group.command(name='list', help='List your active alerts')
async def alert_list(ctx):
    user_id = ctx.author.id
    alerts = get_user_alerts(user_id)

    if not alerts:
        await ctx.send("You don't have any active alerts.")
        return

    result = "🔔 **Your Active Alerts:**\n\n"
    for i, alert in enumerate(alerts):
        # 1-based indexing for user friendliness
        result += f"**ID {i+1}**: {alert['ticker']} {alert['condition']} ${alert['price']:.2f}\n"

    result += "\n*Type `!alert remove <id>` to delete an alert.*"
    await ctx.send(result)

@alert_group.command(name='remove', help='Remove an alert by ID: !alert remove 1')
async def alert_remove(ctx, alert_id: int):
    user_id = ctx.author.id

    # User provides 1-based ID, internal is 0-based
    removed = remove_alert(user_id, alert_id - 1)

    if removed:
        await ctx.send(f"✅ Removed alert for **{removed['ticker']} {removed['condition']} ${removed['price']:.2f}**.")
    else:
        await ctx.send(f"❌ Could not find an alert with ID {alert_id}. Use `!alert list` to see your alerts.")


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

@bot.command(name='chart', aliases=['c'], help='Generates a visual candlestick chart: !chart AAPL')
async def show_chart(ctx, ticker: str):
    await ctx.send(f"📊 Generating chart for **{ticker.upper()}**...")

    # Run the chart generation, which might be slightly blocking
    # For a truly massive bot, this would run in an executor, but it's fine here
    try:
        chart_file = generate_chart(ticker)
        if chart_file == "RATE_LIMITED":
            await ctx.send(f"⚠️ Yahoo Finance rate limit exceeded. Please try again later.")
        elif chart_file:
            await ctx.send(file=chart_file)
        else:
            await ctx.send(f"❌ Could not generate chart for **{ticker.upper()}**. Invalid ticker or no data.")
    except Exception as e:
        await ctx.send(f"❌ Error generating chart: {e}")

@bot.command(name='live', aliases=['price'], help='Shows the live price of a specific stock: !live AAPL')
async def show_live_price(ctx, *tickers):
    if not tickers:
        await ctx.send("Please provide at least one ticker. Example: `!live NVDA AAPL`")
        return

    await ctx.send("Fetching live prices...")

    result_str = "⏱️ **Live Market Prices**\n\n"

    for ticker in tickers[:5]: # Limit to 5 at a time to prevent spam
        ticker = ticker.upper()
        data = get_live_price(ticker)

        if data:
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']

            if change is not None and change_pct is not None:
                emoji = "🟢" if change >= 0 else "🔴"
                sign = "+" if change >= 0 else ""
                result_str += f"**{ticker}**: ${price:.2f} | {emoji} {sign}${change:.2f} ({sign}{change_pct:.2f}%)\n"
            else:
                result_str += f"**{ticker}**: ${price:.2f}\n"
        else:
            result_str += f"**{ticker}**: ⚠️ *Could not fetch data or invalid ticker*\n"

    await ctx.send(result_str)

@bot.command(name='earnings', aliases=['calendar'], help='Shows upcoming earnings for popular tracked tech stocks')
async def show_earnings(ctx):
    await ctx.send("Checking upcoming earnings calendar... 📅")
    from earnings import get_upcoming_earnings
    earnings = get_upcoming_earnings()
    await ctx.send(earnings)

@bot.command(name='insiders', help='Shows the most recent significant insider trades for a ticker: !insiders NVDA')
async def show_insiders(ctx, ticker: str):
    await ctx.send(f"🕵️ Scanning SEC filings for **{ticker.upper()}** insider trades...")
    import asyncio
    from insiders import get_insider_trades
    loop = asyncio.get_event_loop()
    # Run in executor because yfinance can be blocking
    insider_data = await loop.run_in_executor(None, get_insider_trades, ticker)
    await ctx.send(insider_data)

@bot.command(name='whales', aliases=['options', 'flow'], help='Scans for massive unusual options activity')
async def show_whales(ctx):
    await ctx.send("Scanning options chains for whale activity... 🐋 (This takes a moment)")
    from options import scan_unusual_options
    flow = scan_unusual_options()
    await ctx.send(flow)

@bot.command(name='sentiment', aliases=['reddit', 'wsb'], help='Shows top trending stocks on Reddit')
async def show_sentiment(ctx):
    await ctx.send("Scraping r/wallstreetbets for sentiment... 🦍")
    from reddit_sentiment import get_reddit_sentiment
    sentiment = get_reddit_sentiment()
    await ctx.send(sentiment)

@bot.command(name='news', help='Shows a summary of the latest financial news')
async def show_news(ctx):
    await ctx.send("Fetching latest news...")
    summary = get_daily_news_summary()

    # Discord has a 2000 character limit per message, ensure we don't exceed it
    if len(summary) > 2000:
        summary = summary[:1997] + "..."

    await ctx.send(summary)

# --- Background Tasks ---

# Keep track of alerts we've already sent today to avoid spamming the channel
seen_volatility_alerts = set()

@tasks.loop(minutes=30)
async def unusual_activity_scanner():
    """Scans for major price swings and posts to the channel if found."""
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

    alerts = scan_unusual_activity()
    if not alerts:
        return

    new_alerts = []
    for alert in alerts:
        # Create a unique key for today (ticker + direction)
        # In a real production app, we'd reset this set daily at market open
        alert_key = f"{alert['ticker']}_{alert['direction']}"
        if alert_key not in seen_volatility_alerts:
            new_alerts.append(alert)
            seen_volatility_alerts.add(alert_key)

    if new_alerts:
        msg = "⚠️ **[UNUSUAL MARKET ACTIVITY DETECTED]** ⚠️\n\n"
        for a in new_alerts:
            msg += f"**{a['ticker']}** is {a['direction']}! {a['emoji']} {a['change_pct']:.2f}% (Current: ${a['price']:.2f})\n"

        await channel.send(msg)

    # Simple memory management to prevent unbounded growth over weeks
    if len(seen_volatility_alerts) > 500:
        seen_volatility_alerts.clear()

@tasks.loop(minutes=5)
async def check_price_alerts():
    """Iterates through all saved alerts, checks the live price, and DMs users if met."""
    all_alerts = get_all_alerts()
    if not all_alerts:
        return

    for user_id_str, alerts in all_alerts.items():
        if not alerts:
            continue

        user = bot.get_user(int(user_id_str))
        # If user isn't cached, try fetching them
        if user is None:
            try:
                user = await bot.fetch_user(int(user_id_str))
            except Exception:
                continue # User might have left or Discord API error

        # To avoid making dozens of duplicate API calls if a user has multiple alerts
        # for the same ticker, we could cache prices per run, but for simplicity we'll
        # just fetch them individually for now.
        alerts_to_remove = []

        for alert in alerts:
            ticker = alert['ticker']
            target_price = alert['price']
            condition = alert['condition']

            data = get_live_price(ticker)
            if not data or data['price'] is None:
                continue

            current_price = data['price']
            triggered = False

            if condition == '>' and current_price > target_price:
                triggered = True
            elif condition == '<' and current_price < target_price:
                triggered = True

            if triggered:
                try:
                    await user.send(f"🚨 **PRICE ALERT** 🚨\n**{ticker}** has crossed your target!\nCondition: `{condition} ${target_price:.2f}`\nCurrent Price: **${current_price:.2f}**")
                    alerts_to_remove.append(alert)
                except discord.errors.Forbidden:
                    # Can't send DM to this user
                    pass

        # Remove triggered alerts so they don't spam
        for alert in alerts_to_remove:
            remove_alert_by_value(int(user_id_str), alert)

@tasks.loop(minutes=15)
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
