import base64
import json
from email.message import EmailMessage

from googleapiclient.discovery import build
from loguru import logger
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.services.llm_service import FunctionCallParams

from .auth import get_google_credentials

async def get_gmail_emails(params: FunctionCallParams):
    """Return the 2 most recent Gmail messages as JSON."""
    try:
        logger.info("🛠 TOOL CALL: get_gmail_emails() invoked")

        await params.llm.push_frame(TTSSpeakFrame("Let me check your inbox"))

        logger.info("📧 Fetching 2 most recent Gmail emails")

        creds = get_google_credentials()
        service = build('gmail', 'v1', credentials=creds)

        message_ids = service.users().messages().list(
            userId='me',
            maxResults=2
        ).execute().get('messages', [])

        emails_list = []
        for msg in message_ids:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata'
            ).execute()

            snippet = message['snippet']
            headers = message['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            sender = next(h['value'] for h in headers if h['name'] == 'From')

            emails_list.append({
                'snippet': snippet,
                'subject': subject,
                'from': sender
            })

        result = json.dumps(emails_list, indent=2)

        logger.info(f"✅ Gmail emails retrieved: {len(emails_list)} emails")
        await params.result_callback(result)
        return result

    except Exception as e:
        logger.error(f"❌ Failed to get Gmail emails: {e}")
        error_result = f"Error retrieving Gmail emails: {str(e)}"
        await params.result_callback(error_result)
        return error_result


async def send_gmail_email(params: FunctionCallParams):
    """Send an email via Gmail (to, subject, body from params.arguments)."""
    try:
        to = params.arguments.get("to", "")
        subject = params.arguments.get("subject", "")
        body = params.arguments.get("body", "")

        logger.info(f"🛠 TOOL CALL: send_gmail_email() invoked — to={to}, subject={subject}")

        await params.llm.push_frame(TTSSpeakFrame("Sending that email now, sir."))

        creds = get_google_credentials()
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": encoded_message})
            .execute()
        )

        result = json.dumps({"status": "sent", "message_id": sent["id"]})
        logger.info(f"✅ Email sent — Message ID: {sent['id']}")
        await params.result_callback(result)
        return result

    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        error_result = f"Error sending email: {str(e)}"
        await params.result_callback(error_result)
        return error_result
