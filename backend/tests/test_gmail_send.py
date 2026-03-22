"""Quick test script to verify sending an email via Gmail.

Run from the backend directory:
    python -m tests.test_gmail_send
"""

import sys
import os
import base64
from email.message import EmailMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.integrations.google.auth import get_google_credentials
from googleapiclient.discovery import build


def test_send_email():
    print("=" * 60)
    print("GMAIL SEND TEST")
    print("=" * 60)

    # Prompt for details so you don't accidentally spam someone
    to = input("  To (email address): ").strip()
    subject = input("  Subject: ").strip()
    body = input("  Body: ").strip()

    if not to:
        print("  ❌ No recipient provided. Aborting.")
        return

    print()
    print(f"  Sending to:  {to}")
    print(f"  Subject:     {subject}")
    print(f"  Body:        {body}")
    print()

    confirm = input("  Send? [y/N]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    try:
        creds = get_google_credentials()
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject

        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": encoded})
            .execute()
        )

        print()
        print(f"  ✅ Email sent! Message ID: {sent['id']}")

    except Exception as e:
        print(f"  ❌ Failed to send: {e}")


if __name__ == "__main__":
    test_send_email()
