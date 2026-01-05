# Signal Deduplication - Summary

## Problem Solved

Previously, if ASML had a STRONG SELL signal, the bot would send the same alert every 15 minutes:
```
10:00 AM - 🔴 STRONG SELL: ASML at $950
10:15 AM - 🔴 STRONG SELL: ASML at $952
10:30 AM - 🔴 STRONG SELL: ASML at $951
10:45 AM - 🔴 STRONG SELL: ASML at $953
...
```

This would spam your channel with duplicate information.

## Solution Implemented

The bot now uses **smart deduplication** with these rules:

### ✅ Signals ARE Sent When:

1. **First Time** - Stock never triggered this signal before
2. **Signal Flipped** - Changed from BUY to SELL or SELL to BUY
3. **Cooldown Passed** - Enough time elapsed (default: 24 hours)
4. **Price Changed** - Moved >5% since last alert
5. **Forced Check** - You used `/check_force` command

### ❌ Signals ARE NOT Sent When:

- Same signal type
- Within cooldown period
- Price hasn't changed significantly

## Console Output

You'll see clear indicators in the console:

```
Analyzing ASML...
  ✓ STRONG SELL signal detected! (First time signal)
  → Message sent to Telegram

Analyzing ASML... (15 minutes later)
  ~ STRONG SELL signal skipped (Duplicate signal - sent 0.2h ago, price change 0.5%)
  → No message sent

Analyzing ASML... (4 hours later)
  ✓ STRONG SELL signal detected! (Significant price change 6.2% >= 5%)
  → Message sent to Telegram

Analyzing ASML... (next day)
  ✓ STRONG SELL signal detected! (Cooldown period passed 24.5h >= 24h)
  → Message sent to Telegram
```

## How It Works Technically

1. Every signal is saved to SQLite database with timestamp and price
2. Before sending a new signal, bot checks last signal for that stock
3. Applies deduplication rules (flip, cooldown, price change)
4. Only sends if rules allow it
5. Persistent across bot restarts (stored in database)

## Configuration Options

### Set Cooldown Period

```bash
/set_cooldown 24    # Daily reminders (default)
/set_cooldown 12    # Every 12 hours
/set_cooldown 0     # Never repeat (only on flip)
```

### Manual Override

```bash
/check              # Normal check (respects cooldown)
/check_force        # Ignores cooldown, sends all signals
```

## Default Settings

- **Cooldown**: 24 hours
- **Price Change Threshold**: 5%
- **Database**: `fat_wallet.db` (persistent)

## Example Timeline

```
Day 1, 10:00 AM
AAPL: STRONG BUY at $240
→ ✅ Sent (first time)

Day 1, 10:15 AM
AAPL: STRONG BUY at $241
→ ❌ Skipped (duplicate, 0.4% change)

Day 1, 2:00 PM
AAPL: STRONG BUY at $254
→ ✅ Sent (5.8% price increase)

Day 1, 6:00 PM
AAPL: STRONG SELL at $268
→ ✅ Sent (signal flipped)

Day 2, 10:00 AM
AAPL: STRONG SELL at $270
→ ✅ Sent (24h cooldown passed)

Day 2, 10:15 AM
AAPL: STRONG SELL at $271
→ ❌ Skipped (duplicate, 0.4% change)
```

## Benefits

✅ **No Spam**: Channel stays clean with only meaningful alerts
✅ **Important Changes**: Always notified when situation changes
✅ **Daily Reminders**: Don't forget about ongoing opportunities
✅ **Customizable**: Adjust cooldown to your preference
✅ **Override Ready**: Force check when you want full picture

## Database Storage

All signals stored in `signal_history` table:
- Ticker
- Signal type (STRONG BUY/SELL)
- Price
- RPP Score
- Timestamp

Query anytime with `/history` command.

## Testing

Run the test suite to verify deduplication:
```bash
python test_deduplication.py
```

All 8 tests should pass, confirming:
- First time signals work
- Duplicates are skipped
- Signal flips are detected
- Price changes trigger alerts
- Forced checks work
- Cooldown configuration works
