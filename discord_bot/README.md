# Discord Stock Bot

A Discord bot that scans popular stocks and financial news to provide insights on:
- **Undervalued Stocks**: Stocks with low P/E ratios that aren't overbought.
- **Growth Stocks**: Stocks with consistent recent growth.
- **FOMO Stocks**: Overhyped stocks with very high RSI or massive recent spikes to potentially avoid.
- **Major News Alerts**: Automatically detects and posts major financial news (e.g., wars, crashes) in your server.

## Features
- `!undervalued`: Scans and lists top undervalued stocks.
- `!growth`: Scans and lists top growth stocks.
- `!fomo`: Scans and lists top overhyped/FOMO stocks.
- `!news`: Provides a summary of the latest financial news.
- **Automated Alerts**: Checks for major news every 5 minutes.
- **Daily Summaries**: Posts a daily market summary automatically.

## Prerequisites
1. **Python 3.8+** installed on your computer or server.
2. A **Discord Bot Token**.

---

## Step 1: Create a Discord Bot and Get Your Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** in the top right corner. Name it whatever you like (e.g., "StockScout") and click **Create**.
3. On the left sidebar, click on **Bot**.
4. Look for the **Privileged Gateway Intents** section on the Bot page.
   - Toggle **MESSAGE CONTENT INTENT** to ON.
   - Click **Save Changes**.
5. Scroll back up and click the **Reset Token** button to generate your bot's token.
   - **Copy this token immediately and save it somewhere safe.** You will need it for the `.env` file later. Do not share it with anyone.
6. Now, invite the bot to your server:
   - On the left sidebar, click **OAuth2** -> **URL Generator**.
   - Under **Scopes**, check the box for `bot`.
   - Under **Bot Permissions**, check `Send Messages`, `Read Message History`, and `View Channels`.
   - Copy the generated URL at the bottom and paste it into your browser to invite the bot to your Discord server.

---

## Step 2: Install Python and Dependencies

1. If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/) and install it. (Make sure to check "Add Python to PATH" during installation if on Windows).
2. Open your terminal or command prompt and navigate to the directory where you saved these bot files:
   ```bash
   cd path/to/discord_bot
   ```
3. Install the required Python libraries using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 3: Configure the Bot Environment

1. In the `discord_bot` folder, create a file named exactly `.env`.
2. Open the `.env` file in any text editor and add your token and channel ID:

   ```
   DISCORD_TOKEN=your_token_copied_from_step_1
   DISCORD_CHANNEL_ID=your_channel_id_here
   ```

   - Replace `your_token_copied_from_step_1` with your actual bot token.
   - To get your `DISCORD_CHANNEL_ID` (the channel where automated news and daily summaries will be posted):
     - In Discord, go to **User Settings** -> **Advanced** and turn on **Developer Mode**.
     - Right-click the channel in your server where you want the bot to post updates, and click **Copy Channel ID**.
     - Paste that number into the `.env` file.

---

## Step 4: Run the Bot!

1. In your terminal/command prompt, run the bot script:
   ```bash
   python bot.py
   ```
   (On some systems, you might need to use `python3 bot.py`)

2. You should see a message saying `YourBotName has connected to Discord!`.
3. Go to your Discord server and try typing `!news` or `!undervalued` to test it!

## Notes on Rate Limits
This bot uses `yfinance` to pull free stock data. To prevent Yahoo Finance from blocking your IP address for making too many requests at once, the bot currently scans a predefined list of 25 popular major stocks. You can edit the `POPULAR_TICKERS` list in `stock_data.py` to add or remove specific stocks you want the bot to track.