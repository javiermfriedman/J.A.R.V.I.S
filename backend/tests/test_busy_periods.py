"""Test script for fetchBusyPeriods — gets busy time slots for a date range.

Run from the backend directory:
    python -m tests.test_busy_periods
"""

import sys
import os
import json
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

from services.google.auth import get_google_credentials
from googleapiclient.discovery import build


def test_busy_periods():
    print()
    print("=" * 60)
    print("📅 TEST: fetchBusyPeriods")
    print("=" * 60)

    # 1. Authenticate
    try:
        creds = get_google_credentials()
        print(f"  ✅ Authenticated")
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        return

    # 2. Prompt for date range (default: today → tomorrow)
    now = datetime.now()
    default_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    default_end = default_start + timedelta(days=1)

    print()
    print(f"  Default range: {default_start.strftime('%Y-%m-%d %H:%M')} → {default_end.strftime('%Y-%m-%d %H:%M')}")
    print()
    custom = input("  Use default range? [Y/n]: ").strip().lower()

    if custom == "n":
        start_str = input("  Start (YYYY-MM-DD): ").strip()
        end_str = input("  End   (YYYY-MM-DD): ").strip()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            print("  ❌ Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        start_date = default_start.astimezone(timezone.utc)
        end_date = default_end.astimezone(timezone.utc)

    print()
    print(f"  Querying: {start_date.isoformat()} → {end_date.isoformat()}")
    print()

    # 3. Query freebusy API
    try:
        service = build('calendar', 'v3', credentials=creds)

        body = {
            "timeMin": start_date.isoformat(),
            "timeMax": end_date.isoformat(),
            "timeZone": "America/New_York",
            "items": [{"id": "primary"}],
        }

        result = service.freebusy().query(body=body).execute()
        calendars = result.get('calendars', {})
        busy_periods = calendars.get("primary", {}).get('busy', [])

        print(f"  Busy periods found: {len(busy_periods)}")
        print()

        if not busy_periods:
            print("  📭 No busy periods — calendar is clear!")
            return

        for i, period in enumerate(busy_periods, 1):
            start_dt = datetime.fromisoformat(period['start'].replace('Z', '+00:00')).astimezone()
            end_dt = datetime.fromisoformat(period['end'].replace('Z', '+00:00')).astimezone()
            print(f"  {i}. {start_dt.strftime('%I:%M %p')} – {end_dt.strftime('%I:%M %p')}")

        print()
        print("  JSON output (what the bot would see):")
        print(json.dumps(busy_periods, indent=2))

    except Exception as e:
        print(f"  ❌ Failed: {e}")


if __name__ == "__main__":
    test_busy_periods()
