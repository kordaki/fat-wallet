# Fat Wallet Market Bot

A Telegram bot that monitors stock market signals using Bollinger Bands and Relative Price Position (RPP) analysis to alert you on potential buy/sell opportunities.

## ✨ Version 2 Features (Enhanced)

- **SQLite Database Caching**: Fast analysis with 95% reduction in API calls
- **Smart Signal Deduplication**: Prevents duplicate alerts, only notifies on important changes
- **Admin Commands**: Manage watchlist and settings via Telegram
- **Dynamic Configuration**: Change thresholds and intervals on-the-fly
- **Signal History**: Track all buy/sell alerts over time
- **Smart Updates**: Daily data refresh instead of constant API calls
- Monitors stocks with Bollinger Bands and RPP analysis
- Sends Telegram alerts only when signals are detected
- Customizable check intervals and thresholds

## Stock Watchlist

**Tech Leaders:**
- NVDA (Nvidia)
- GOOGL (Google)
- ASML (ASML)
- AAPL (Apple)
- AMZN (Amazon)

**2026 World Cup Plays:**
- ADS.DE (Adidas - Official ball/kit provider)
- V (Visa - Official payment partner)
- KO (Coca-Cola - Major sponsor)

## Signal Logic

### STRONG BUY
Triggers when BOTH conditions are met:
- Current price < Lower Bollinger Band
- RPP Score < 10%

### STRONG SELL
Triggers when BOTH conditions are met:
- Current price > Upper Bollinger Band
- RPP Score > 90%

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with your bot token and channel ID:
```
TELEGRAM_BOT_TOKEN=8573028822:AAGLvpsvmNUGcuOGZ7QL8ui5UlV7Ks7luOg
TELEGRAM_CHAT_ID=-1003544900612
```

## Usage

### Run the Bot (Version 2 - Recommended)

```bash
source venv/bin/activate
python market_bot_v2.py
```

This version includes:
- Database caching for faster analysis
- Admin commands via Telegram
- Signal history tracking
- Dynamic configuration

### Run the Original Bot (Version 1)

```bash
source venv/bin/activate
python market_bot.py
```

Simple version without database or admin commands.

The bot will:
1. Send a startup notification to your Telegram channel
2. Check all stocks in the watchlist
3. Send alerts when signals are detected
4. Repeat every 15 minutes

### Run Tests

```bash
source venv/bin/activate
python test_bot.py
```

This will verify:
- Data fetching from Yahoo Finance
- RPP calculations
- Bollinger Bands calculations
- Signal detection logic
- Telegram message formatting

### Stop the Bot

Press `Ctrl+C` to stop the bot gracefully.

## Customization

### Change Check Interval

Edit `market_bot.py` and modify:
```python
CHECK_INTERVAL = 900  # 15 minutes in seconds
```

### Adjust Signal Thresholds

Edit `market_bot.py`:
```python
RPP_BUY_THRESHOLD = 10   # Buy if RPP < 10%
RPP_SELL_THRESHOLD = 90  # Sell if RPP > 90%
```

### Modify Watchlist

Edit the `WATCHLIST` array in `market_bot.py`:
```python
WATCHLIST = [
    'NVDA',
    'GOOGL',
    # Add or remove tickers here
]
```

## Technical Details

### Relative Price Position (RPP)

```
RPP = ((Current Price - Min Price) / (Max Price - Min Price)) * 100
```

- Uses last 180 days (or available data) of highs and lows
- 0% = at 6-month low
- 100% = at 6-month high

### Bollinger Bands

- Middle Band: 20-day Simple Moving Average (SMA)
- Upper Band: SMA + (2 × Standard Deviation)
- Lower Band: SMA - (2 × Standard Deviation)

## Admin Commands

Version 2 includes powerful admin commands. See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for complete documentation.

**Quick Reference:**
- `/watchlist` - View stocks being monitored
- `/add TICKER [NAME]` - Add a stock
- `/remove TICKER` - Remove a stock
- `/settings` - View current configuration
- `/set_interval MINUTES` - Change check frequency
- `/set_buy PERCENT` - Adjust buy threshold
- `/set_sell PERCENT` - Adjust sell threshold
- `/check` - Run immediate analysis
- `/history` - View recent signals

**Admin User ID:** 1937651844

## File Structure

```
fat-wallet/
├── .env                 # Bot credentials (DO NOT COMMIT)
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── database.py         # Database management (V2)
├── market_bot.py       # Original bot (V1)
├── market_bot_v2.py    # Enhanced bot with admin commands (V2)
├── test_bot.py         # Test suite (V1)
├── test_bot_v2.py      # Test suite (V2)
├── fat_wallet.db       # SQLite database (created on first run)
├── ADMIN_GUIDE.md      # Complete admin command guide
└── README.md           # This file
```

## Troubleshooting

### Bot not sending messages

1. Check that your bot token is correct in `.env`
2. Verify the bot is an admin in the channel
3. Check the chat ID is correct (should start with `-`)

### No data for certain stocks

Some stocks may not have data available through Yahoo Finance. Check the ticker symbol is correct.

### Too many/few alerts

Adjust the `RPP_BUY_THRESHOLD` and `RPP_SELL_THRESHOLD` values to be more or less conservative.

## Security Note

The `.env` file contains sensitive credentials and is excluded from git via `.gitignore`. Never commit this file to version control.