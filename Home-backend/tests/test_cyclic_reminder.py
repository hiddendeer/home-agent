# -*- coding: utf-8 -*-
"""Test cyclic hydration reminder logic.

Scenarios:
1. User drinks water, after 10 hours -> should trigger reminder
2. After another 10 hours (20 total) -> should trigger reminder again
3. After another 10 hours (30 total) -> should trigger reminder again
4. User drinks water -> restart timer
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import app.infrastructure.database as db
from app.models.behavior import Behavior
from app.models.user import User
from app.services.hydration_service import HydrationService
from app.utils.datetime import calculate_minutes_ago


async def test_cyclic_reminder():
    """Test cyclic reminder logic."""
    print("=" * 60)
    print("Test Cyclic Hydration Reminder Logic")
    print("=" * 60)

    # Initialize database
    db.init_mysql()

    async with db.async_session_maker() as session:
        service = HydrationService(session)

        # Get or create test user
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalars().first()

        if not user:
            user = User(
                username="test_user",
                email="test@example.com",
                hashed_password="test",
                full_name="Test User"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"[OK] Created test user: {user.id}\n")

        user_id = user.id

        # Scenario 1: User drank water 10 hours ago, should trigger reminder
        print("Scenario 1: User drank water 10 hours ago (600 minutes)")
        print("-" * 60)

        # Clear previous reminder record
        user.last_hydration_remind_at = None

        # Clear old drink records
        old_behaviors = await session.execute(
            select(Behavior).where(Behavior.user_id == user_id, Behavior.action_type == "drink_water")
        )
        for old_behavior in old_behaviors.scalars().all():
            await session.delete(old_behavior)
        await session.commit()

        # Create drink record from 10 hours ago
        drink_time_10h = datetime.now() - timedelta(minutes=600)
        behavior = Behavior(
            user_id=user_id,
            device_id="test_device",
            action_type="drink_water",
            details={"amount": "200ml"},
            raw_content="drink water 200ml",
            timestamp=drink_time_10h
        )
        session.add(behavior)
        await session.commit()
        await session.refresh(behavior)
        print(f"  Created drink record: {behavior.timestamp}")

        # Execute check
        now = datetime.now()
        should_remind = await service.check_and_remind(user_id, now)

        # Verify result
        last_drink_time = await service._get_last_drink_time(user_id)
        minutes_since = calculate_minutes_ago(last_drink_time, now)

        print(f"  Minutes since last drink: {minutes_since:.1f}")
        print(f"  Should remind: {should_remind}")

        if should_remind:
            print("  [PASS] Scenario 1 passed: Reminder triggered after 10 hours\n")
        else:
            print("  [FAIL] Scenario 1 failed: Should trigger reminder but didn't\n")
            return False

        # Scenario 2: After another 10 hours (20 total), should trigger again
        print("Scenario 2: 20 hours since last drink (1200 minutes)")
        print("-" * 60)

        # Update drink record to 20 hours ago
        behavior.timestamp = datetime.now() - timedelta(minutes=1200)
        await session.commit()

        now = datetime.now()
        should_remind = await service.check_and_remind(user_id, now)

        last_drink_time = await service._get_last_drink_time(user_id)
        minutes_since = calculate_minutes_ago(last_drink_time, now)
        last_remind_time = await service._get_last_remind_time(user_id)
        minutes_since_remind = calculate_minutes_ago(last_remind_time, now) if last_remind_time else 0

        print(f"  Minutes since last drink: {minutes_since:.1f}")
        print(f"  Minutes since last remind: {minutes_since_remind:.1f}")
        print(f"  Should remind: {should_remind}")

        if should_remind:
            print("  [PASS] Scenario 2 passed: Reminder triggered again after 20 hours\n")
        else:
            print("  [FAIL] Scenario 2 failed: Should trigger reminder again but didn't\n")
            print("  This is the root cause of 2.14-2.24 no reminder issue!")
            return False

        # Scenario 3: After another 10 hours (30 total), should trigger third time
        print("Scenario 3: 30 hours since last drink (1800 minutes)")
        print("-" * 60)

        # Update drink record to 30 hours ago
        behavior.timestamp = datetime.now() - timedelta(minutes=1800)
        await session.commit()

        now = datetime.now()
        should_remind = await service.check_and_remind(user_id, now)

        last_drink_time = await service._get_last_drink_time(user_id)
        minutes_since = calculate_minutes_ago(last_drink_time, now)

        print(f"  Minutes since last drink: {minutes_since:.1f}")
        print(f"  Should remind: {should_remind}")

        if should_remind:
            print("  [PASS] Scenario 3 passed: Reminder triggered third time after 30 hours\n")
        else:
            print("  [FAIL] Scenario 3 failed: Should trigger third reminder but didn't\n")
            return False

        # Scenario 4: User drinks water, restart timer
        print("Scenario 4: User drinks water, restart timer")
        print("-" * 60)

        # Create new drink record (5 minutes ago)
        new_drink_time = datetime.now() - timedelta(minutes=5)
        new_behavior = Behavior(
            user_id=user_id,
            device_id="test_device",
            action_type="drink_water",
            details={"amount": "200ml"},
            raw_content="drink water 200ml",
            timestamp=new_drink_time
        )
        session.add(new_behavior)
        await session.commit()

        now = datetime.now()
        should_remind = await service.check_and_remind(user_id, now)

        last_drink_time = await service._get_last_drink_time(user_id)
        minutes_since = calculate_minutes_ago(last_drink_time, now)

        print(f"  Minutes since last drink: {minutes_since:.1f}")
        print(f"  Should remind: {should_remind}")

        if not should_remind:
            print("  [PASS] Scenario 4 passed: No reminder right after drinking\n")
        else:
            print("  [FAIL] Scenario 4 failed: Should not trigger right after drinking\n")
            return False

    print("=" * 60)
    print("[SUCCESS] All tests passed! Cyclic reminder logic works correctly")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_cyclic_reminder())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        asyncio.run(db.close_mysql())
