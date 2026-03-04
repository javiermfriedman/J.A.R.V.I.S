"""Quick test script to verify Google Calendar & Gmail integration.

Run from the backend directory:
    python -m tests.test_google
"""

import json
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure backend/ is on the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

from services.google_calender import get_google_credentials, SCOPES
from googleapiclient.discovery import build


def test_credentials():
    """Test that we can authenticate with Google."""
    print("=" * 60)
    print("1. TESTING GOOGLE CREDENTIALS")
    print("=" * 60)
    try:
        creds = get_google_credentials()
        print(f"  ✅ Authenticated successfully")
        print(f"  Token valid: {creds.valid}")
        print(f"  Scopes: {creds.scopes}")
        return creds
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        return None


def test_calendar(creds):
    """Fetch and display today's calendar events."""
    print()
    print("=" * 60)
    print("2. TESTING CALENDAR EVENTS (today)")
    print("=" * 60)
    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        time_min = today_start.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        time_max = today_end.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

        print(f"  Date: {now.strftime('%A %B %d, %Y')}")
        print(f"  Range: {time_min} → {time_max}")
        print()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print(f"  Raw events returned: {len(events)}")
        print()

        if not events:
            print("  📭 No events found for today.")
            return

        for i, event in enumerate(events, 1):
            summary = event.get('summary', 'Untitled Event')
            start_dt_str = event.get('start', {}).get('dateTime')
            start_date_str = event.get('start', {}).get('date')

            if start_dt_str:
                start_dt = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00')).astimezone()
                end_dt_str = event.get('end', {}).get('dateTime')
                end_dt = datetime.fromisoformat(end_dt_str.replace('Z', '+00:00')).astimezone()
                time_str = f"{start_dt.strftime('%I:%M %p')} – {end_dt.strftime('%I:%M %p')}"
            elif start_date_str:
                time_str = "All day"
            else:
                time_str = "Unknown time"

            print(f"  {i}. {summary}")
            print(f"     {time_str}")
            print()

    except Exception as e:
        print(f"  ❌ Calendar fetch failed: {e}")


def test_gmail(creds):
    """Fetch and display the 2 most recent emails."""
    print()
    print("=" * 60)
    print("3. TESTING GMAIL (2 most recent)")
    print("=" * 60)
    try:
        service = build('gmail', 'v1', credentials=creds)

        message_ids = service.users().messages().list(
            userId='me',
            maxResults=2
        ).execute().get('messages', [])

        print(f"  Messages returned: {len(message_ids)}")
        print()

        for i, msg in enumerate(message_ids, 1):
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata'
            ).execute()

            snippet = message.get('snippet', '')
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(no subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(unknown)')

            print(f"  {i}. From: {sender}")
            print(f"     Subject: {subject}")
            print(f"     Snippet: {snippet[:100]}{'...' if len(snippet) > 100 else ''}")
            print()

    except Exception as e:
        print(f"  ❌ Gmail fetch failed: {e}")


if __name__ == "__main__":
    print()
    print("🔧 J.A.R.V.I.S. Google Services Test")
    print()

    creds = test_credentials()
    if not creds:
        print("\nCannot proceed without credentials. Exiting.")
        sys.exit(1)

    test_calendar(creds)
    test_gmail(creds)

    print("=" * 60)
    print("Done.")
    print("=" * 60)
