from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo
from resume_agent.orchestrate.scheduler import (
    IST,
    SCHEDULED_SLOTS,
    get_next_slot,
    seconds_until_next_slot,
)


def test_scheduled_slots_count_and_timing():
    """Verify exactly 4 daily slots are defined with proper IST times and digest flag."""
    assert len(SCHEDULED_SLOTS) == 4

    times = [s[0] for s in SCHEDULED_SLOTS]
    assert times == [
        dtime(9, 0),    # 09:00 AM IST
        dtime(13, 30),  # 01:30 PM IST
        dtime(17, 30),  # 05:30 PM IST
        dtime(21, 0),   # 09:00 PM IST
    ]

    # Only 09:00 PM (slot 4) should have is_digest = True
    assert SCHEDULED_SLOTS[0][2] is False
    assert SCHEDULED_SLOTS[1][2] is False
    assert SCHEDULED_SLOTS[2][2] is False
    assert SCHEDULED_SLOTS[3][2] is True


def test_get_next_slot_early_morning():
    """At 07:00 AM IST, the next slot should be 09:00 AM IST."""
    test_dt = datetime(2026, 9, 23, 7, 0, tzinfo=IST)
    next_dt, label, is_digest = get_next_slot(test_dt)

    assert next_dt.hour == 9
    assert next_dt.minute == 0
    assert is_digest is False
    assert "Morning" in label


def test_get_next_slot_midday():
    """At 10:00 AM IST, the next slot should be 01:30 PM IST."""
    test_dt = datetime(2026, 9, 23, 10, 0, tzinfo=IST)
    next_dt, label, is_digest = get_next_slot(test_dt)

    assert next_dt.hour == 13
    assert next_dt.minute == 30
    assert is_digest is False
    assert "Afternoon" in label


def test_get_next_slot_afternoon():
    """At 02:00 PM IST, the next slot should be 05:30 PM IST."""
    test_dt = datetime(2026, 9, 23, 14, 0, tzinfo=IST)
    next_dt, label, is_digest = get_next_slot(test_dt)

    assert next_dt.hour == 17
    assert next_dt.minute == 30
    assert is_digest is False
    assert "Evening" in label


def test_get_next_slot_evening_pre_digest():
    """At 06:00 PM IST, the next slot should be 09:00 PM IST with is_digest=True."""
    test_dt = datetime(2026, 9, 23, 18, 0, tzinfo=IST)
    next_dt, label, is_digest = get_next_slot(test_dt)

    assert next_dt.hour == 21
    assert next_dt.minute == 0
    assert is_digest is True
    assert "Night Finale" in label


def test_get_next_slot_late_night_rollover():
    """At 10:00 PM IST (after 09:00 PM), next slot should roll over to tomorrow 09:00 AM IST."""
    test_dt = datetime(2026, 9, 23, 22, 0, tzinfo=IST)
    next_dt, label, is_digest = get_next_slot(test_dt)

    assert next_dt.day == 24
    assert next_dt.hour == 9
    assert next_dt.minute == 0
    assert is_digest is False


def test_seconds_until_next_slot():
    """Verify calculated seconds until next slot is non-negative and accurate."""
    test_dt = datetime(2026, 9, 23, 8, 0, tzinfo=IST)  # 1 hour before 09:00 AM
    delay, label, is_digest = seconds_until_next_slot(test_dt)

    assert delay == 3600.0
    assert "Morning" in label
