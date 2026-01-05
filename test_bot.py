"""
Test script to verify the market bot functionality.
"""
import asyncio
from market_bot import (
    fetch_stock_data,
    calculate_rpp,
    calculate_bollinger_bands,
    analyze_stock,
    format_signal_message
)


def test_data_fetch():
    """Test fetching stock data."""
    print("Testing data fetch for AAPL...")
    df = fetch_stock_data('AAPL', period='6mo')

    if df is not None and not df.empty:
        print(f"✓ Successfully fetched {len(df)} days of data")
        print(f"  Latest close price: ${df['Close'].iloc[-1]:.2f}")
        return True
    else:
        print("✗ Failed to fetch data")
        return False


def test_rpp_calculation():
    """Test RPP calculation."""
    print("\nTesting RPP calculation for NVDA...")
    df = fetch_stock_data('NVDA', period='6mo')

    if df is not None:
        rpp_score, current_price = calculate_rpp(df)

        if rpp_score is not None:
            print(f"✓ RPP Score: {rpp_score:.2f}%")
            print(f"  Current Price: ${current_price:.2f}")
            return True
        else:
            print("✗ Failed to calculate RPP")
            return False
    else:
        print("✗ Failed to fetch data")
        return False


def test_bollinger_bands():
    """Test Bollinger Bands calculation."""
    print("\nTesting Bollinger Bands for GOOGL...")
    df = fetch_stock_data('GOOGL', period='6mo')

    if df is not None:
        upper, middle, lower, current = calculate_bollinger_bands(df)

        if upper is not None:
            print(f"✓ Bollinger Bands calculated:")
            print(f"  Upper: ${upper:.2f}")
            print(f"  Middle: ${middle:.2f}")
            print(f"  Lower: ${lower:.2f}")
            print(f"  Current: ${current:.2f}")
            return True
        else:
            print("✗ Failed to calculate Bollinger Bands")
            return False
    else:
        print("✗ Failed to fetch data")
        return False


def test_stock_analysis():
    """Test complete stock analysis."""
    print("\nTesting complete analysis for AAPL...")
    analysis = analyze_stock('AAPL')

    if analysis:
        print(f"✓ Signal detected: {analysis['signal']}")
        print(f"  {analysis['ticker']} - ${analysis['current_price']:.2f}")
        print(f"  RPP: {analysis['rpp_score']:.2f}%")
    else:
        print("- No signal (this is normal if no buy/sell conditions are met)")

    return True


async def test_telegram_message():
    """Test Telegram message formatting."""
    print("\nTesting message formatting...")

    # Create a mock analysis result
    mock_analysis = {
        'ticker': 'TEST',
        'signal': 'STRONG BUY',
        'current_price': 150.25,
        'rpp_score': 8.5,
        'upper_band': 160.0,
        'middle_band': 150.0,
        'lower_band': 140.0,
        'triggers': [
            'Price below Lower Bollinger Band ($140.00)',
            'RPP Score (8.50%) < 10%'
        ]
    }

    message = format_signal_message(mock_analysis)
    print("✓ Message formatted successfully:")
    print("-" * 50)
    print(message)
    print("-" * 50)

    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Fat Wallet Market Bot - Test Suite")
    print("=" * 60)

    tests = [
        ("Data Fetch", test_data_fetch),
        ("RPP Calculation", test_rpp_calculation),
        ("Bollinger Bands", test_bollinger_bands),
        ("Stock Analysis", test_stock_analysis),
        ("Message Formatting", test_telegram_message),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
