"""Test script for scheduleEvent — books a new Google Calendar event.

Run from the backend directory:
    python -m tests.test_schedule_event
"""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.integrations.google.auth import get_google_credentials
from googleapiclient.discovery import build


def test_schedule_event():
    print()
    print("=" * 60)
    print("📅 TEST: scheduleEvent")
    print("=" * 60)

    try:
        creds = get_google_credentials()
        print(f"  ✅ Authenticated")
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        return

    print()
    summary = input("  Event title: ").strip()
    if not summary:
        print("  ❌ Title is required. Aborting.")
        return

    description = input("  Description (optional): ").strip()
    location = input("  Location (optional): ").strip()
    attendee_email = input("  Attendee email (optional): ").strip()

    print()
    print("  Enter start time (leave blank for 1 hour from now):")
    start_str = input("  Start (YYYY-MM-DD HH:MM): ").strip()

    if start_str:
        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("  ❌ Invalid format. Use YYYY-MM-DD HH:MM")
            return
    else:
        start_dt = datetime.now().replace(second=0, microsecond=0) + timedelta(hours=1)

    duration_str = input("  Duration in minutes (default 60): ").strip()
    duration = int(duration_str) if duration_str.isdigit() else 60
    end_dt = start_dt + timedelta(minutes=duration)

    tz = "America/New_York"

    print()
    print("  " + "-" * 40)
    print(f"  Title:       {summary}")
    print(f"  Description: {description or '(none)'}")
    print(f"  Location:    {location or '(none)'}")
    print(f"  Attendee:    {attendee_email or '(none)'}")
    print(f"  Start:       {start_dt.strftime('%A %B %d, %Y %I:%M %p')}")
    print(f"  End:         {end_dt.strftime('%A %B %d, %Y %I:%M %p')}")
    print(f"  Timezone:    {tz}")
    print("  " + "-" * 40)
    print()

    confirm = input("  Book this event? [y/N]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    try:
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': tz,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': tz,
            },
            'sendNotifications': True,
        }

        if attendee_email:
            event['attendees'] = [{'email': attendee_email}]

        created = service.events().insert(calendarId='primary', body=event).execute()

        print()
        print(f"  ✅ Event booked!")
        print(f"  Event ID: {created.get('id')}")
        print(f"  Link:     {created.get('htmlLink')}")
        print()
        print("  JSON output (what the bot would see):")
        print(json.dumps(event, indent=2))

    except Exception as e:
        print(f"  ❌ Failed: {e}")


if __name__ == "__main__":
    test_schedule_event()
