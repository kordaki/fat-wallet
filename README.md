# Fat Wallet Market Bot

A Telegram bot that monitors stock market signals using Bollinger Bands and Relative Price Position (RPP) analysis to alert you on potential buy/sell opportunities.

## Features

- Monitors 8 stocks including tech leaders and 2026 World Cup sponsors
- Calculates Bollinger Bands (20-day SMA with 2 standard deviations)
- Calculates Relative Price Position (RPP) based on 6-month highs/lows
- Sends Telegram alerts when STRONG BUY or STRONG SELL signals are detected
- Runs every 15 minutes automatically

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

### Run the Bot

```bash
source venv/bin/activate
python market_bot.py
```

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

## File Structure

```
fat-wallet/
├── .env                 # Bot credentials (DO NOT COMMIT)
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── market_bot.py       # Main bot script
├── test_bot.py         # Test suite
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