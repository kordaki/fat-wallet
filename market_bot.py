import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
from telegram import Bot

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Watchlist: Tech leaders + 2026 World Cup plays
WATCHLIST = [
    'NVDA',      # Nvidia
    'GOOGL',     # Google
    'ASML',      # ASML
    'AAPL',      # Apple
    'AMZN',      # Amazon
    'ADS.DE',    # Adidas (World Cup)
    'V',         # Visa (World Cup payment partner)
    'KO',        # Coca-Cola (World Cup sponsor)
]

# Alert thresholds
RPP_BUY_THRESHOLD = 10   # Buy if RPP < 10%
RPP_SELL_THRESHOLD = 90  # Sell if RPP > 90%
CHECK_INTERVAL = 900     # 15 minutes in seconds


def fetch_stock_data(ticker, period='6mo'):
    """
    Fetch historical stock data using yfinance.
    Returns a pandas DataFrame with OHLCV data.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            print(f"No data fetched for {ticker}")
            return None

        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def calculate_rpp(df):
    """
    Calculate Relative Price Position (RPP).
    Formula: ((Current - Min) / (Max - Min)) * 100

    Returns the RPP score and the current price.
    """
    if df is None or len(df) < 20:
        return None, None

    # Use all available data (up to 180 days)
    df_180 = df.tail(180) if len(df) >= 180 else df

    min_price = df_180['Low'].min()
    max_price = df_180['High'].max()
    current_price = df_180['Close'].iloc[-1]

    if max_price == min_price:
        return None, current_price

    rpp_score = ((current_price - min_price) / (max_price - min_price)) * 100

    return rpp_score, current_price


def calculate_bollinger_bands(df, window=20, num_std=2):
    """
    Calculate Bollinger Bands.
    Formula:
    - Middle Band: 20-day SMA
    - Upper Band: SMA + (2 * Standard Deviation)
    - Lower Band: SMA - (2 * Standard Deviation)

    Returns upper_band, middle_band, lower_band, and current_price.
    """
    if df is None or len(df) < window:
        return None, None, None, None

    close_prices = df['Close']

    # Calculate SMA and standard deviation
    sma = close_prices.rolling(window=window).mean()
    std_dev = close_prices.rolling(window=window).std()

    # Calculate bands
    upper_band = sma + (std_dev * num_std)
    lower_band = sma - (std_dev * num_std)

    # Get latest values
    current_price = close_prices.iloc[-1]
    upper = upper_band.iloc[-1]
    middle = sma.iloc[-1]
    lower = lower_band.iloc[-1]

    return upper, middle, lower, current_price


def analyze_stock(ticker):
    """
    Analyze a stock and generate buy/sell signals.

    Returns a dictionary with signal information or None if no signal.
    """
    # Fetch data
    df = fetch_stock_data(ticker)

    if df is None:
        return None

    # Calculate indicators
    rpp_score, current_price = calculate_rpp(df)
    upper_band, middle_band, lower_band, _ = calculate_bollinger_bands(df)

    if rpp_score is None or lower_band is None:
        return None

    # Determine signal
    signal = None
    trigger = []

    # STRONG BUY conditions
    if current_price < lower_band and rpp_score < RPP_BUY_THRESHOLD:
        signal = 'STRONG BUY'
        trigger.append(f'Price below Lower Bollinger Band (${lower_band:.2f})')
        trigger.append(f'RPP Score ({rpp_score:.2f}%) < {RPP_BUY_THRESHOLD}%')

    # STRONG SELL conditions
    elif current_price > upper_band and rpp_score > RPP_SELL_THRESHOLD:
        signal = 'STRONG SELL'
        trigger.append(f'Price above Upper Bollinger Band (${upper_band:.2f})')
        trigger.append(f'RPP Score ({rpp_score:.2f}%) > {RPP_SELL_THRESHOLD}%')

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


async def send_telegram_message(message):
    """
    Send a message to the configured Telegram channel.
    """
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print(f"Message sent successfully at {datetime.now()}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


def format_signal_message(analysis):
    """
    Format the analysis results into a Telegram message.
    """
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


async def check_all_stocks():
    """
    Check all stocks in the watchlist and send alerts if signals are detected.
    """
    print(f"\n{'='*60}")
    print(f"Checking stocks at {datetime.now()}")
    print(f"{'='*60}")

    for ticker in WATCHLIST:
        print(f"Analyzing {ticker}...")

        analysis = analyze_stock(ticker)

        if analysis:
            print(f"  ✓ {analysis['signal']} signal detected!")
            message = format_signal_message(analysis)
            await send_telegram_message(message)
        else:
            print(f"  - No signal")

    print(f"\nNext check in {CHECK_INTERVAL // 60} minutes...")


async def main():
    """
    Main loop that continuously monitors the watchlist.
    """
    print("=" * 60)
    print("Fat Wallet Market Bot Started")
    print("=" * 60)
    print(f"Watchlist: {', '.join(WATCHLIST)}")
    print(f"Check interval: {CHECK_INTERVAL // 60} minutes")
    print(f"RPP Buy threshold: < {RPP_BUY_THRESHOLD}%")
    print(f"RPP Sell threshold: > {RPP_SELL_THRESHOLD}%")
    print("=" * 60)

    # Send startup notification
    startup_message = "🤖 *Fat Wallet Bot Started*\n\n"
    startup_message += f"Monitoring {len(WATCHLIST)} stocks:\n"
    startup_message += f"{', '.join(WATCHLIST)}\n\n"
    startup_message += f"Check interval: {CHECK_INTERVAL // 60} minutes"

    await send_telegram_message(startup_message)

    while True:
        try:
            await check_all_stocks()
            await asyncio.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    asyncio.run(main())
