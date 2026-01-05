# Quick Start Guide

Get your Fat Wallet bot running in 5 minutes!

## Step 1: Start the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Run the enhanced version (recommended)
python market_bot_v2.py
```

You should see:
```
Starting bot...
✓ Database initialized
============================================================
Fat Wallet Market Bot Started
============================================================
Watchlist: 8 stocks
Check interval: 15 minutes
============================================================
```

## Step 2: Test Admin Commands

Open Telegram and find your bot. Send these commands:

```
/start
```

You'll see the admin panel with all available commands.

```
/watchlist
```

This shows all 8 stocks currently being monitored.

```
/settings
```

This shows your current configuration:
- Check Interval: 15 minutes
- Buy Threshold: < 10%
- Sell Threshold: > 90%

## Step 3: Watch for Signals

The bot will automatically:
1. Check all stocks every 15 minutes
2. Send Telegram messages ONLY when a STRONG BUY or STRONG SELL signal is detected
3. Print status to console

**Console output:**
```
============================================================
Checking stocks at 2026-01-05 23:00:00
============================================================
Analyzing NVDA...
  Using cached data for NVDA
  - No signal
Analyzing GOOGL...
  Using cached data for GOOGL
  - No signal
Analyzing AAPL...
  Using cached data for AAPL
  ✓ STRONG BUY signal detected!
...
Next check in 15 minutes...
```

**Telegram message (only when signal detected):**
```
🟢 STRONG BUY: AAPL

💰 Current Price: $240.50
📊 RPP Score: 8.25%
📈 Bollinger Bands:
   Upper: $265.00
   Middle: $250.00
   Lower: $235.00

⚡ Triggers:
   • Price below Lower Bollinger Band ($235.00)
   • RPP Score (8.25%) < 10%

🕐 2026-01-05 23:00:00
```

## Step 4: Customize Your Settings

Try these common adjustments:

### Add a new stock
```
/add TSLA Tesla
```

### Change check frequency to 30 minutes
```
/set_interval 30
```

### Make buy signals more aggressive (< 5%)
```
/set_buy 5
```

### Run an immediate check
```
/check
```

## Understanding Signals

### STRONG BUY 🟢
The bot sends this when **BOTH** conditions are met:
1. Current price is **below** the Lower Bollinger Band (oversold)
2. RPP Score is **< 10%** (near 6-month low)

This suggests the stock might be undervalued and could bounce back.

### STRONG SELL 🔴
The bot sends this when **BOTH** conditions are met:
1. Current price is **above** the Upper Bollinger Band (overbought)
2. RPP Score is **> 90%** (near 6-month high)

This suggests the stock might be overvalued and could pull back.

## What's Happening Behind the Scenes

### First Run
- Creates SQLite database (`fat_wallet.db`)
- Downloads 6 months of data for all 8 stocks
- Caches the data locally
- Takes ~20-30 seconds

### Subsequent Runs
- Uses cached data (instant!)
- Only downloads new data once per day
- Takes ~2-3 seconds per check

### Database Benefits
- 95% reduction in API calls
- Much faster analysis
- Tracks signal history
- Stores configuration

## Common Tasks

### View Recent Signals
```
/history
```

### Adjust Sensitivity

**Get MORE alerts** (less strict):
```
/set_buy 15
/set_sell 85
```

**Get FEWER alerts** (more strict):
```
/set_buy 5
/set_sell 95
```

### Focus on Specific Stocks

Remove everything and add only what you want:
```
/remove ASML
/remove ADS.DE
/remove KO
/add TSLA Tesla
/add MSFT Microsoft
```

## Stopping the Bot

Press `Ctrl+C` in the terminal:
```
^C
Bot stopped by user
```

The database and all settings are preserved for next time.

## Next Steps

- Read [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for detailed command documentation
- Read [README.md](README.md) for technical details
- Experiment with different thresholds to find what works for you
- Monitor the console for real-time status updates

## Tips for Success

1. **Start Conservative**: Use default settings (10% buy, 90% sell) for the first week
2. **Monitor Console**: Watch the console output to see how often signals trigger
3. **Adjust Gradually**: Change thresholds by 5% at a time
4. **Track History**: Use `/history` to see which stocks are most active
5. **Don't Panic**: These are just signals, not financial advice!

## Troubleshooting

### Not getting any messages?
- Bot only sends messages when signals are detected
- Check console output to verify bot is running
- Try `/check` to force an immediate analysis
- Lower thresholds temporarily: `/set_buy 20` and `/set_sell 80`

### Bot stopped working?
- Check if the terminal is still running
- Restart: `python market_bot_v2.py`
- Check internet connection

### Commands not working?
- Make sure you're using the correct admin Telegram account
- Only user ID `1937651844` has access
- Check for typos in commands

## Need Help?

All your settings are stored in the database. You can:
- Stop and restart the bot anytime
- Change settings on the fly
- View history of all signals
- Add/remove stocks dynamically

Happy trading! 📈
