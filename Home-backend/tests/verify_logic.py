# -*- coding: utf-8 -*-
"""Verify the cyclic reminder logic manually."""

from datetime import datetime, timedelta

def calculate_minutes_ago(start_time, end_time):
    """Calculate minutes between two datetimes."""
    delta = end_time - start_time
    return delta.total_seconds() / 60

def test_logic():
    """Test the reminder logic."""
    print("=" * 60)
    print("Verify Cyclic Reminder Logic")
    print("=" * 60)

    # Scenario: User drinks at 20:57
    drink_time = datetime(2026, 2, 14, 20, 57, 0)
    print(f"\nUser drinks water at: {drink_time}")
    print()

    # Scenario 1: 10 hours later (06:57 next day)
    check_time_1 = drink_time + timedelta(hours=10)
    minutes_since_1 = calculate_minutes_ago(drink_time, check_time_1)
    minutes_since_remind_1 = 9999  # No previous reminder

    should_remind_1 = (minutes_since_1 >= 600) and (minutes_since_remind_1 >= 590)

    print(f"Scenario 1: {check_time_1} (10 hours later)")
    print(f"  Minutes since drink: {minutes_since_1:.1f}")
    print(f"  Minutes since last remind: {minutes_since_remind_1:.1f}")
    print(f"  Should remind: {should_remind_1}")
    print(f"  Result: {'[PASS]' if should_remind_1 else '[FAIL]'}\n")

    # First reminder sent at check_time_1
    last_remind_time = check_time_1

    # Scenario 2: 20 hours total (16:57 next day)
    check_time_2 = drink_time + timedelta(hours=20)
    minutes_since_2 = calculate_minutes_ago(drink_time, check_time_2)
    minutes_since_remind_2 = calculate_minutes_ago(last_remind_time, check_time_2)

    should_remind_2 = (minutes_since_2 >= 600) and (minutes_since_remind_2 >= 590)

    print(f"Scenario 2: {check_time_2} (20 hours total)")
    print(f"  Minutes since drink: {minutes_since_2:.1f}")
    print(f"  Minutes since last remind: {minutes_since_remind_2:.1f}")
    print(f"  Should remind: {should_remind_2}")
    print(f"  Result: {'[PASS]' if should_remind_2 else '[FAIL]'}")
    if not should_remind_2:
        print("  This would cause the 2.14-2.24 no reminder issue!\n")
    else:
        print()

    # Second reminder sent at check_time_2
    last_remind_time = check_time_2

    # Scenario 3: 30 hours total (02:57 day after)
    check_time_3 = drink_time + timedelta(hours=30)
    minutes_since_3 = calculate_minutes_ago(drink_time, check_time_3)
    minutes_since_remind_3 = calculate_minutes_ago(last_remind_time, check_time_3)

    should_remind_3 = (minutes_since_3 >= 600) and (minutes_since_remind_3 >= 590)

    print(f"Scenario 3: {check_time_3} (30 hours total)")
    print(f"  Minutes since drink: {minutes_since_3:.1f}")
    print(f"  Minutes since last remind: {minutes_since_remind_3:.1f}")
    print(f"  Should remind: {should_remind_3}")
    print(f"  Result: {'[PASS]' if should_remind_3 else '[FAIL]'}\n")

    # Third reminder sent at check_time_3
    last_remind_time = check_time_3

    # Scenario 4: 240 hours total (10 days later, like 2.14 to 2.24)
    check_time_4 = drink_time + timedelta(hours=240)
    minutes_since_4 = calculate_minutes_ago(drink_time, check_time_4)
    minutes_since_remind_4 = calculate_minutes_ago(last_remind_time, check_time_4)

    should_remind_4 = (minutes_since_4 >= 600) and (minutes_since_remind_4 >= 590)

    print(f"Scenario 4: {check_time_4} (240 hours total, 10 days)")
    print(f"  Minutes since drink: {minutes_since_4:.1f}")
    print(f"  Minutes since last remind: {minutes_since_remind_4:.1f}")
    print(f"  Should remind: {should_remind_4}")
    print(f"  Result: {'[PASS]' if should_remind_4 else '[FAIL]'}")
    if not should_remind_4:
        print("  This would cause the 2.14-2.24 no reminder issue!\n")
    else:
        print()

    print("=" * 60)
    all_pass = should_remind_1 and should_remind_2 and should_remind_3 and should_remind_4
    if all_pass:
        print("[SUCCESS] All scenarios pass! The fix is correct.")
    else:
        print("[FAIL] Some scenarios fail. The logic needs more work.")
    print("=" * 60)

    return all_pass

if __name__ == "__main__":
    test_logic()
