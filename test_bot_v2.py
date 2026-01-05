"""
Test script for the enhanced market bot with database caching.
"""
import database as db
from market_bot_v2 import fetch_and_cache_stock_data, calculate_rpp, analyze_stock


def test_database_init():
    """Test database initialization."""
    print("Testing database initialization...")
    db.init_database()
    print("✓ Database initialized successfully\n")


def test_config():
    """Test configuration management."""
    print("Testing configuration...")

    # Get default config
    interval = db.get_config('check_interval')
    buy_threshold = db.get_config('rpp_buy_threshold')
    sell_threshold = db.get_config('rpp_sell_threshold')
    admin_id = db.get_config('admin_user_id')

    print(f"✓ Check interval: {interval} seconds")
    print(f"✓ Buy threshold: {buy_threshold}%")
    print(f"✓ Sell threshold: {sell_threshold}%")
    print(f"✓ Admin user ID: {admin_id}")

    # Test setting config
    db.set_config('check_interval', 1800)
    new_interval = db.get_config('check_interval')
    assert new_interval == '1800'

    # Reset
    db.set_config('check_interval', 900)
    print("✓ Configuration read/write working\n")


def test_watchlist():
    """Test watchlist management."""
    print("Testing watchlist management...")

    # Get initial watchlist
    watchlist = db.get_watchlist()
    print(f"✓ Initial watchlist has {len(watchlist)} stocks")

    # Add a test stock
    success = db.add_to_watchlist('MSFT', 'Microsoft')
    if success:
        print("✓ Added MSFT to watchlist")
    else:
        print("- MSFT already in watchlist")

    # Try adding duplicate (should fail)
    success = db.add_to_watchlist('MSFT', 'Microsoft')
    if not success:
        print("✓ Duplicate prevention working")

    # Remove test stock
    success = db.remove_from_watchlist('MSFT')
    if success:
        print("✓ Removed MSFT from watchlist")

    print()


def test_data_caching():
    """Test stock data caching."""
    print("Testing data caching...")

    ticker = 'AAPL'

    # First fetch (should hit API)
    print(f"First fetch of {ticker}...")
    df1 = fetch_and_cache_stock_data(ticker)

    if df1 is not None:
        print(f"✓ Fetched {len(df1)} days of data")

        # Check if data was saved
        last_date = db.get_last_cached_date(ticker)
        print(f"✓ Latest cached date: {last_date}")

        # Second fetch (should use cache)
        print(f"Second fetch of {ticker}...")
        df2 = fetch_and_cache_stock_data(ticker)

        if df2 is not None:
            print(f"✓ Retrieved {len(df2)} days from cache")

        # Check needs_update
        needs_update = db.needs_update(ticker)
        print(f"✓ Needs update: {needs_update}")
    else:
        print("✗ Failed to fetch data")

    print()


def test_analysis():
    """Test stock analysis with cached data."""
    print("Testing stock analysis with caching...")

    ticker = 'NVDA'
    analysis = analyze_stock(ticker)

    if analysis:
        print(f"✓ Signal detected for {ticker}: {analysis['signal']}")
        print(f"  Price: ${analysis['current_price']:.2f}")
        print(f"  RPP: {analysis['rpp_score']:.2f}%")
    else:
        print(f"- No signal for {ticker} (this is normal)")

    print()


def test_signal_history():
    """Test signal history."""
    print("Testing signal history...")

    # Save a test signal
    db.save_signal('TEST', 'STRONG BUY', 150.25, 8.5)
    print("✓ Saved test signal")

    # Retrieve history
    history = db.get_signal_history(days=30)
    print(f"✓ Retrieved {len(history)} signals from history")

    if history:
        latest = history[0]
        print(f"  Latest: {latest[0]} - {latest[1]} at ${latest[2]:.2f}")

    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Fat Wallet Market Bot V2 - Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Database Initialization", test_database_init),
        ("Configuration Management", test_config),
        ("Watchlist Management", test_watchlist),
        ("Data Caching", test_data_caching),
        ("Stock Analysis", test_analysis),
        ("Signal History", test_signal_history),
    ]

    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}\n")

    print("=" * 60)
    print("Test Suite Completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
