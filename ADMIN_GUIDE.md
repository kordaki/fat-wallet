# Fat Wallet Bot - Admin Guide

This guide explains how to use the admin commands to manage your Fat Wallet bot.

## Admin User

Your Telegram user ID `1937651844` has full admin access to the bot.

## Getting Started

1. **Start a chat with your bot** on Telegram
2. Send `/start` to see all available commands

## Admin Commands Reference

### View Information

#### `/watchlist`
View all stocks currently being monitored.

**Example:**
```
/watchlist
```

**Response:**
```
📊 Current Watchlist

• NVDA (Nvidia)
• GOOGL (Google)
• AAPL (Apple)
...

Total: 8 stocks
```

---

#### `/settings`
View current bot configuration.

**Example:**
```
/settings
```

**Response:**
```
⚙️ Current Settings

🕐 Check Interval: 15 minutes
📉 Buy Threshold: < 10%
📈 Sell Threshold: > 90%
```

---

#### `/history`
View recent buy/sell signals from the last 7 days.

**Example:**
```
/history
```

**Response:**
```
📜 Recent Signals (Last 7 Days)

🟢 NVDA - STRONG BUY
   $188.12 | RPP: 8.5%
   2026-01-05 14:30:00

🔴 AAPL - STRONG SELL
   $267.26 | RPP: 92.3%
   2026-01-04 10:15:00
```

---

### Manage Watchlist

#### `/add TICKER [NAME]`
Add a new stock to the watchlist.

**Examples:**
```
/add TSLA
/add TSLA Tesla
/add META Meta Platforms
```

**Response:**
```
✅ Added TSLA to watchlist (Tesla)
```

---

#### `/remove TICKER`
Remove a stock from the watchlist.

**Example:**
```
/remove TSLA
```

**Response:**
```
✅ Removed TSLA from watchlist
```

---

### Configure Settings

#### `/set_interval MINUTES`
Change how often the bot checks stocks.

**Examples:**
```
/set_interval 15    # Check every 15 minutes
/set_interval 30    # Check every 30 minutes
/set_interval 60    # Check every hour
```

**Response:**
```
✅ Check interval updated to 30 minutes
```

**Note:** The bot will automatically restart the monitoring with the new interval.

---

#### `/set_buy PERCENT`
Change the RPP buy threshold (0-100).

**Examples:**
```
/set_buy 10    # Buy when RPP < 10%
/set_buy 5     # More aggressive (buy when RPP < 5%)
/set_buy 15    # Less aggressive (buy when RPP < 15%)
```

**Response:**
```
✅ Buy threshold updated to < 5%
```

---

#### `/set_sell PERCENT`
Change the RPP sell threshold (0-100).

**Examples:**
```
/set_sell 90    # Sell when RPP > 90%
/set_sell 95    # More conservative (sell when RPP > 95%)
/set_sell 85    # Less conservative (sell when RPP > 85%)
```

**Response:**
```
✅ Sell threshold updated to > 95%
```

---

### Manual Actions

#### `/check`
Trigger an immediate check of all stocks (doesn't wait for the next scheduled check).

**Example:**
```
/check
```

**Response:**
```
🔄 Running immediate check...
✅ Check completed
```

---

## Understanding RPP Thresholds

### Buy Threshold
- **Lower = More Aggressive**: A threshold of 5% means buy when the price is in the bottom 5% of its 6-month range
- **Higher = Less Aggressive**: A threshold of 15% means buy when the price is in the bottom 15%

**Recommended:** 5-10% for strong buy signals

### Sell Threshold
- **Higher = More Conservative**: A threshold of 95% means sell when the price is in the top 5% of its 6-month range
- **Lower = Less Conservative**: A threshold of 85% means sell when the price is in the top 15%

**Recommended:** 90-95% for strong sell signals

---

## Common Workflows

### Adding a New Stock

1. Research the ticker symbol (e.g., TSLA for Tesla)
2. Add to watchlist:
   ```
   /add TSLA Tesla
   ```
3. Optionally run an immediate check:
   ```
   /check
   ```

### Adjusting Sensitivity

**To get MORE alerts (riskier):**
```
/set_buy 15
/set_sell 85
```

**To get FEWER alerts (safer):**
```
/set_buy 5
/set_sell 95
```

### Checking Performance

1. View recent signals:
   ```
   /history
   ```
2. Review which stocks are triggering alerts
3. Remove underperforming stocks if needed:
   ```
   /remove TICKER
   ```

### Changing Check Frequency

**For active trading:**
```
/set_interval 5    # Check every 5 minutes
```

**For casual monitoring:**
```
/set_interval 60   # Check every hour
```

**For daily checks:**
```
/set_interval 1440 # Check once per day (24 hours)
```

---

## Tips and Best Practices

### Watchlist Size
- **Recommended:** 5-15 stocks
- More stocks = more API calls and longer check times
- Focus on stocks you're seriously considering

### Check Interval
- **Market hours:** 5-15 minutes for active monitoring
- **After hours:** 30-60 minutes to reduce unnecessary checks
- Consider using different intervals based on market volatility

### Threshold Tuning
- Start with defaults (10% buy, 90% sell)
- Monitor for a week
- Adjust based on whether you're getting too many/few alerts
- Different stocks have different volatility profiles

### Data Caching
- The bot caches stock data to reduce API calls
- Cache updates automatically once per day
- Use `/check` to force a fresh analysis with latest cached data

---

## Troubleshooting

### Not receiving alerts?

1. Check current settings:
   ```
   /settings
   ```
2. Make thresholds less strict:
   ```
   /set_buy 20
   /set_sell 80
   ```
3. Run manual check:
   ```
   /check
   ```

### Too many alerts?

1. Make thresholds stricter:
   ```
   /set_buy 5
   /set_sell 95
   ```
2. Reduce watchlist to only high-conviction stocks

### Stock not showing signals?

1. Check if it's in the watchlist:
   ```
   /watchlist
   ```
2. The stock might just not meet the criteria
3. Check signal history to see if it triggered in the past:
   ```
   /history
   ```

---

## Advanced Usage

### Monitoring Specific Sectors

Create focused watchlists by removing all stocks and adding only sector-specific ones:

**Tech sector:**
```
/add NVDA Nvidia
/add GOOGL Google
/add MSFT Microsoft
/add AAPL Apple
```

**World Cup 2026:**
```
/add ADS.DE Adidas
/add V Visa
/add KO Coca-Cola
/add DAL Delta
```

### Seasonal Adjustments

**Before earnings season:**
```
/set_interval 5      # More frequent checks
/set_buy 8           # Slightly more aggressive
```

**During low volatility:**
```
/set_interval 60     # Less frequent checks
/set_buy 12          # Less strict
```

---

## Need Help?

- All commands are case-insensitive
- Ticker symbols should be valid Yahoo Finance tickers
- The bot only responds to the configured admin user ID
- Check console output for detailed logging
