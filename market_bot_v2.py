import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

import database as db

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def is_admin(user_id):
    """Check if user is admin."""
    admin_id = db.get_config('admin_user_id')
    return str(user_id) == str(admin_id)


def fetch_and_cache_stock_data(ticker):
    """
    Fetch stock data and cache it. Uses cached data if available and recent.
    """
    # Check if we need to update
    if not db.needs_update(ticker):
        print(f"  Using cached data for {ticker}")
        return db.get_cached_stock_data(ticker)

    # Fetch fresh data from API
    print(f"  Fetching fresh data for {ticker}")
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='6mo')

        if df.empty:
            print(f"  No data fetched for {ticker}")
            # Try to use cached data even if old
            return db.get_cached_stock_data(ticker)

        # Save to cache
        db.save_stock_data(ticker, df)
        return df

    except Exception as e:
        print(f"  Error fetching data for {ticker}: {e}")
        # Fall back to cached data
        return db.get_cached_stock_data(ticker)


def calculate_rpp(df):
    """Calculate Relative Price Position (RPP)."""
    if df is None or len(df) < 20:
        return None, None

    df_180 = df.tail(180) if len(df) >= 180 else df

    min_price = df_180['Low'].min()
    max_price = df_180['High'].max()
    current_price = df_180['Close'].iloc[-1]

    if max_price == min_price:
        return None, current_price

    rpp_score = ((current_price - min_price) / (max_price - min_price)) * 100
    return rpp_score, current_price


def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands."""
    if df is None or len(df) < window:
        return None, None, None, None

    close_prices = df['Close']
    sma = close_prices.rolling(window=window).mean()
    std_dev = close_prices.rolling(window=window).std()

    upper_band = sma + (std_dev * num_std)
    lower_band = sma - (std_dev * num_std)

    current_price = close_prices.iloc[-1]
    upper = upper_band.iloc[-1]
    middle = sma.iloc[-1]
    lower = lower_band.iloc[-1]

    return upper, middle, lower, current_price


def analyze_stock(ticker):
    """Analyze a stock and generate buy/sell signals."""
    df = fetch_and_cache_stock_data(ticker)

    if df is None:
        return None

    # Get thresholds from config
    rpp_buy = float(db.get_config('rpp_buy_threshold'))
    rpp_sell = float(db.get_config('rpp_sell_threshold'))

    rpp_score, current_price = calculate_rpp(df)
    upper_band, middle_band, lower_band, _ = calculate_bollinger_bands(df)

    if rpp_score is None or lower_band is None:
        return None

    signal = None
    trigger = []

    # STRONG BUY conditions
    if current_price < lower_band and rpp_score < rpp_buy:
        signal = 'STRONG BUY'
        trigger.append(f'Price below Lower Bollinger Band (${lower_band:.2f})')
        trigger.append(f'RPP Score ({rpp_score:.2f}%) < {rpp_buy}%')

    # STRONG SELL conditions
    elif current_price > upper_band and rpp_score > rpp_sell:
        signal = 'STRONG SELL'
        trigger.append(f'Price above Upper Bollinger Band (${upper_band:.2f})')
        trigger.append(f'RPP Score ({rpp_score:.2f}%) > {rpp_sell}%')

    if signal:
        return {
            'ticker': ticker,
            'signal': signal,
            'current_price': current_price,
            'rpp_score': rpp_score,
            'lower_band': lower_band,
            'upper_band': upper_band,
            'middle_band': middle_band,
            'triggers': trigger
        }

    return None


async def send_telegram_message(message, bot=None):
    """Send a message to the configured Telegram channel."""
    try:
        if bot is None:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print(f"Message sent successfully at {datetime.now()}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


def format_signal_message(analysis):
    """Format the analysis results into a Telegram message."""
    ticker = analysis['ticker']
    signal = analysis['signal']
    price = analysis['current_price']
    rpp = analysis['rpp_score']

    emoji = "🟢" if signal == "STRONG BUY" else "🔴"

    message = f"{emoji} *{signal}: {ticker}*\n\n"
    message += f"💰 Current Price: ${price:.2f}\n"
    message += f"📊 RPP Score: {rpp:.2f}%\n"
    message += f"📈 Bollinger Bands:\n"
    message += f"   Upper: ${analysis['upper_band']:.2f}\n"
    message += f"   Middle: ${analysis['middle_band']:.2f}\n"
    message += f"   Lower: ${analysis['lower_band']:.2f}\n\n"
    message += f"⚡ Triggers:\n"

    for trigger in analysis['triggers']:
        message += f"   • {trigger}\n"

    message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return message


# Admin command handlers
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not is_admin(update.effective_user.id):
        return

    message = "🤖 *Fat Wallet Bot - Admin Panel*\n\n"
    message += "*Available Commands:*\n"
    message += "/watchlist - View current watchlist\n"
    message += "/add TICKER NAME - Add stock to watchlist\n"
    message += "/remove TICKER - Remove stock from watchlist\n"
    message += "/analyze TICKER - Analyze any stock instantly\n"
    message += "/settings - View current settings\n"
    message += "/set\\_interval MINUTES - Set check interval\n"
    message += "/set\\_buy PERCENT - Set buy threshold\n"
    message += "/set\\_sell PERCENT - Set sell threshold\n"
    message += "/set\\_cooldown HOURS - Set signal cooldown\n"
    message += "/check - Run immediate check\n"
    message += "/check\\_force - Force check (ignore cooldown)\n"
    message += "/history - View recent signals"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /watchlist command."""
    if not is_admin(update.effective_user.id):
        return

    watchlist = db.get_watchlist()

    message = "📊 *Current Watchlist*\n\n"
    for ticker, name in watchlist:
        name_display = f" ({name})" if name else ""
        message += f"• {ticker}{name_display}\n"

    message += f"\n*Total: {len(watchlist)} stocks*"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /add TICKER [NAME]")
        return

    ticker = context.args[0].upper()
    name = ' '.join(context.args[1:]) if len(context.args) > 1 else None

    if db.add_to_watchlist(ticker, name):
        message = f"✅ Added *{ticker}* to watchlist"
        if name:
            message += f" ({name})"
    else:
        message = f"❌ *{ticker}* is already in the watchlist"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /remove TICKER")
        return

    ticker = context.args[0].upper()

    if db.remove_from_watchlist(ticker):
        message = f"✅ Removed *{ticker}* from watchlist"
    else:
        message = f"❌ *{ticker}* not found in watchlist"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    if not is_admin(update.effective_user.id):
        return

    interval = int(db.get_config('check_interval'))
    buy_threshold = db.get_config('rpp_buy_threshold')
    sell_threshold = db.get_config('rpp_sell_threshold')
    cooldown_hours = float(db.get_config('signal_cooldown_hours'))
    price_change = db.get_config('price_change_threshold')

    message = "⚙️ *Current Settings*\n\n"
    message += f"🕐 Check Interval: *{interval // 60} minutes*\n"
    message += f"📉 Buy Threshold: *< {buy_threshold}%*\n"
    message += f"📈 Sell Threshold: *> {sell_threshold}%*\n"

    if cooldown_hours == 0:
        message += f"⏱️ Signal Cooldown: *Disabled*\n"
    else:
        message += f"⏱️ Signal Cooldown: *{cooldown_hours} hours*\n"

    message += f"💹 Price Change Alert: *{price_change}%*\n\n"
    message += "Use /set\\_interval, /set\\_buy, /set\\_sell, or /set\\_cooldown to modify"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_interval command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /set_interval MINUTES")
        return

    try:
        minutes = int(context.args[0])
        if minutes < 1:
            raise ValueError()

        seconds = minutes * 60
        db.set_config('check_interval', seconds)

        message = f"✅ Check interval updated to *{minutes} minutes*"
        await update.message.reply_text(message, parse_mode='Markdown')

        # Restart the monitoring task
        if 'monitor_task' in context.bot_data:
            context.bot_data['monitor_task'].cancel()
            context.bot_data['monitor_task'] = asyncio.create_task(
                monitor_stocks(context.bot)
            )

    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number of minutes")


async def cmd_set_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_buy command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /set_buy PERCENT")
        return

    try:
        threshold = float(context.args[0])
        if threshold < 0 or threshold > 100:
            raise ValueError()

        db.set_config('rpp_buy_threshold', threshold)
        message = f"✅ Buy threshold updated to *< {threshold}%*"
        await update.message.reply_text(message, parse_mode='Markdown')

    except ValueError:
        await update.message.reply_text("❌ Please provide a valid percentage (0-100)")


async def cmd_set_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_sell command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /set_sell PERCENT")
        return

    try:
        threshold = float(context.args[0])
        if threshold < 0 or threshold > 100:
            raise ValueError()

        db.set_config('rpp_sell_threshold', threshold)
        message = f"✅ Sell threshold updated to *> {threshold}%*"
        await update.message.reply_text(message, parse_mode='Markdown')

    except ValueError:
        await update.message.reply_text("❌ Please provide a valid percentage (0-100)")


async def cmd_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check command - run immediate stock check."""
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text("🔄 Running immediate check...")
    await check_all_stocks(context.bot, force=False)
    await update.message.reply_text("✅ Check completed")


async def cmd_check_force(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check_force command - run check ignoring cooldown."""
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text("🔄 Running FORCED check (ignoring cooldown)...")
    await check_all_stocks(context.bot, force=True)
    await update.message.reply_text("✅ Forced check completed")


async def cmd_set_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_cooldown command."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /set_cooldown HOURS\n\nSet to 0 to disable cooldown (never repeat same signal)")
        return

    try:
        hours = float(context.args[0])
        if hours < 0:
            raise ValueError()

        db.set_config('signal_cooldown_hours', hours)

        if hours == 0:
            message = "✅ Cooldown disabled - signals will only be sent once (until they flip)"
        else:
            message = f"✅ Signal cooldown updated to *{hours} hours*"

        await update.message.reply_text(message, parse_mode='Markdown')

    except ValueError:
        await update.message.reply_text("❌ Please provide a valid number of hours (0 or greater)")


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command - analyze a specific stock on demand."""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /analyze TICKER\n\nExample: /analyze TSLA")
        return

    ticker = context.args[0].upper()

    await update.message.reply_text(f"🔍 Analyzing *{ticker}*...", parse_mode='Markdown')

    # Run analysis
    analysis = analyze_stock(ticker)

    # Get thresholds for context
    rpp_buy = float(db.get_config('rpp_buy_threshold'))
    rpp_sell = float(db.get_config('rpp_sell_threshold'))

    if analysis:
        # Stock has a signal
        signal_type = analysis['signal']
        emoji = "🟢" if signal_type == "STRONG BUY" else "🔴"

        message = f"{emoji} *{ticker} - {signal_type}*\n\n"
        message += f"💰 Current Price: ${analysis['current_price']:.2f}\n"
        message += f"📊 RPP Score: {analysis['rpp_score']:.2f}%\n\n"
        message += f"📈 Bollinger Bands:\n"
        message += f"   Upper: ${analysis['upper_band']:.2f}\n"
        message += f"   Middle: ${analysis['middle_band']:.2f}\n"
        message += f"   Lower: ${analysis['lower_band']:.2f}\n\n"
        message += f"⚡ Triggers:\n"
        for trigger in analysis['triggers']:
            message += f"   • {trigger}\n"
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    else:
        # No signal - show neutral analysis
        df = fetch_and_cache_stock_data(ticker)

        if df is None or df.empty:
            await update.message.reply_text(f"❌ Could not fetch data for *{ticker}*\n\nPlease check the ticker symbol.", parse_mode='Markdown')
            return

        rpp_score, current_price = calculate_rpp(df)
        upper_band, middle_band, lower_band, _ = calculate_bollinger_bands(df)

        if rpp_score is None or lower_band is None:
            await update.message.reply_text(f"❌ Insufficient data to analyze *{ticker}*", parse_mode='Markdown')
            return

        # Determine status
        if current_price < lower_band:
            bb_status = "Below Lower Band (Oversold)"
            bb_emoji = "📉"
        elif current_price > upper_band:
            bb_status = "Above Upper Band (Overbought)"
            bb_emoji = "📈"
        else:
            bb_status = "Within Bands (Normal)"
            bb_emoji = "➡️"

        if rpp_score < rpp_buy:
            rpp_status = f"Near Low ({rpp_score:.1f}% < {rpp_buy}%)"
        elif rpp_score > rpp_sell:
            rpp_status = f"Near High ({rpp_score:.1f}% > {rpp_sell}%)"
        else:
            rpp_status = f"Mid-Range ({rpp_score:.1f}%)"

        message = f"ℹ️ *{ticker} - No Signal*\n\n"
        message += f"💰 Current Price: ${current_price:.2f}\n"
        message += f"📊 RPP Score: {rpp_score:.2f}%\n"
        message += f"   Status: {rpp_status}\n\n"
        message += f"📈 Bollinger Bands:\n"
        message += f"   Upper: ${upper_band:.2f}\n"
        message += f"   Middle: ${middle_band:.2f}\n"
        message += f"   Lower: ${lower_band:.2f}\n"
        message += f"   {bb_emoji} Status: {bb_status}\n\n"
        message += f"💡 *Why No Signal?*\n"

        if current_price >= lower_band and rpp_score >= rpp_buy:
            message += f"   • Price not oversold enough\n"
            message += f"   • RPP not low enough for BUY\n"
        elif current_price <= upper_band and rpp_score <= rpp_sell:
            message += f"   • Price not overbought enough\n"
            message += f"   • RPP not high enough for SELL\n"
        else:
            message += f"   • Both conditions not met\n"

        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    if not is_admin(update.effective_user.id):
        return

    history = db.get_signal_history(days=7)

    if not history:
        await update.message.reply_text("No signals in the last 7 days")
        return

    message = "📜 *Recent Signals (Last 7 Days)*\n\n"
    for ticker, signal_type, price, rpp_score, created_at in history[:10]:
        emoji = "🟢" if signal_type == "STRONG BUY" else "🔴"
        message += f"{emoji} *{ticker}* - {signal_type}\n"
        message += f"   ${price:.2f} | RPP: {rpp_score:.1f}%\n"
        message += f"   {created_at}\n\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def check_all_stocks(bot, force=False):
    """Check all stocks in the watchlist and send alerts if signals are detected."""
    print(f"\n{'='*60}")
    print(f"Checking stocks at {datetime.now()}")
    if force:
        print("FORCED CHECK - Ignoring cooldown")
    print(f"{'='*60}")

    watchlist = db.get_watchlist()

    for ticker, name in watchlist:
        print(f"Analyzing {ticker}...")

        analysis = analyze_stock(ticker)

        if analysis:
            # Check if we should send this signal (deduplication)
            should_send, reason = db.should_send_signal(
                ticker,
                analysis['signal'],
                analysis['current_price'],
                force=force
            )

            if should_send:
                print(f"  ✓ {analysis['signal']} signal detected! ({reason})")

                # Save to history
                db.save_signal(
                    ticker,
                    analysis['signal'],
                    analysis['current_price'],
                    analysis['rpp_score']
                )

                # Send alert
                message = format_signal_message(analysis)
                await send_telegram_message(message, bot)
            else:
                print(f"  ~ {analysis['signal']} signal skipped ({reason})")
        else:
            print(f"  - No signal")

    interval = int(db.get_config('check_interval'))
    print(f"\nNext check in {interval // 60} minutes...")


async def monitor_stocks(bot):
    """Background task that continuously monitors stocks."""
    while True:
        try:
            await check_all_stocks(bot)
            interval = int(db.get_config('check_interval'))
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            await asyncio.sleep(60)


async def post_init(application: Application):
    """Initialize bot after startup."""
    # Initialize database
    db.init_database()

    # Send startup notification
    watchlist = db.get_watchlist()
    interval = int(db.get_config('check_interval'))

    startup_message = "🤖 *Fat Wallet Bot Started*\n\n"
    startup_message += f"Monitoring {len(watchlist)} stocks:\n"
    startup_message += f"{', '.join([t for t, _ in watchlist])}\n\n"
    startup_message += f"Check interval: {interval // 60} minutes"

    await send_telegram_message(startup_message, application.bot)

    # Start monitoring task
    application.bot_data['monitor_task'] = asyncio.create_task(
        monitor_stocks(application.bot)
    )

    print("=" * 60)
    print("Fat Wallet Market Bot Started")
    print("=" * 60)
    print(f"Watchlist: {len(watchlist)} stocks")
    print(f"Check interval: {interval // 60} minutes")
    print("=" * 60)


async def post_shutdown(application: Application):
    """Cleanup on shutdown."""
    if 'monitor_task' in application.bot_data:
        application.bot_data['monitor_task'].cancel()


def main():
    """Main entry point."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("watchlist", cmd_watchlist))
    application.add_handler(CommandHandler("add", cmd_add))
    application.add_handler(CommandHandler("remove", cmd_remove))
    application.add_handler(CommandHandler("analyze", cmd_analyze))
    application.add_handler(CommandHandler("settings", cmd_settings))
    application.add_handler(CommandHandler("set_interval", cmd_set_interval))
    application.add_handler(CommandHandler("set_buy", cmd_set_buy))
    application.add_handler(CommandHandler("set_sell", cmd_set_sell))
    application.add_handler(CommandHandler("set_cooldown", cmd_set_cooldown))
    application.add_handler(CommandHandler("check", cmd_check))
    application.add_handler(CommandHandler("check_force", cmd_check_force))
    application.add_handler(CommandHandler("history", cmd_history))

    # Start bot
    print("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
