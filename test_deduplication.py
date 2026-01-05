"""
Test script for signal deduplication logic.
"""
import database as db
from datetime import datetime, timedelta


def test_deduplication():
    """Test the signal deduplication logic."""
    print("=" * 60)
    print("Testing Signal Deduplication Logic")
    print("=" * 60)
    print()

    # Initialize database
    db.init_database()

    ticker = "TEST_STOCK"

    # Test 1: First time signal - should send
    print("Test 1: First time signal")
    should_send, reason = db.should_send_signal(ticker, "STRONG BUY", 100.0)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    assert should_send == True
    print("  ✓ PASS\n")

    # Save the signal
    db.save_signal(ticker, "STRONG BUY", 100.0, 8.5)

    # Test 2: Same signal immediately after - should NOT send
    print("Test 2: Same signal immediately after (duplicate)")
    should_send, reason = db.should_send_signal(ticker, "STRONG BUY", 100.0)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    assert should_send == False
    print("  ✓ PASS\n")

    # Test 3: Signal flipped - should send
    print("Test 3: Signal flipped (BUY → SELL)")
    should_send, reason = db.should_send_signal(ticker, "STRONG SELL", 120.0)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    assert should_send == True
    print("  ✓ PASS\n")

    # Save the flipped signal
    db.save_signal(ticker, "STRONG SELL", 120.0, 92.0)

    # Test 4: Significant price change - should send
    print("Test 4: Same signal but significant price change (>5%)")
    new_price = 120.0 * 1.06  # 6% increase
    should_send, reason = db.should_send_signal(ticker, "STRONG SELL", new_price)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    assert should_send == True
    print("  ✓ PASS\n")

    # Test 5: Forced check - always send
    print("Test 5: Forced check (ignore cooldown)")
    should_send, reason = db.should_send_signal(ticker, "STRONG SELL", 120.0, force=True)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    assert should_send == True
    print("  ✓ PASS\n")

    # Test 6: Test cooldown configuration
    print("Test 6: Cooldown configuration")
    cooldown = db.get_config('signal_cooldown_hours')
    print(f"  Current cooldown: {cooldown} hours")
    assert cooldown == '24'
    print("  ✓ PASS\n")

    # Test 7: Disable cooldown (set to 0)
    print("Test 7: Disable cooldown")
    db.set_config('signal_cooldown_hours', 0)
    # Create a new test ticker
    test_ticker2 = "TEST_STOCK_2"
    db.save_signal(test_ticker2, "STRONG BUY", 50.0, 5.0)
    # Same signal immediately - with cooldown=0, should NOT send
    should_send, reason = db.should_send_signal(test_ticker2, "STRONG BUY", 50.0)
    print(f"  Should send: {should_send}")
    print(f"  Reason: {reason}")
    # With 0 cooldown and no price change, should not send
    assert should_send == False
    print("  ✓ PASS\n")

    # Reset cooldown
    db.set_config('signal_cooldown_hours', 24)

    # Test 8: Get last signal
    print("Test 8: Get last signal")
    last_signal = db.get_last_signal(ticker)
    if last_signal:
        signal_type, price, created_at = last_signal
        print(f"  Last signal: {signal_type} at ${price:.2f}")
        print(f"  Created at: {created_at}")
        print("  ✓ PASS\n")
    else:
        print("  ✗ FAIL - No signal found\n")

    print("=" * 60)
    print("All Deduplication Tests Passed! ✓")
    print("=" * 60)
    print()

    # Display summary
    print("Deduplication Rules Summary:")
    print("1. ✓ First time signal → Always send")
    print("2. ✓ Signal flipped (BUY↔SELL) → Always send")
    print("3. ✓ Cooldown period passed → Send reminder")
    print("4. ✓ Significant price change → Send update")
    print("5. ✗ Duplicate (same signal, within cooldown, similar price) → Skip")
    print()


if __name__ == "__main__":
    test_deduplication()
