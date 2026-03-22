from pipecat.frames.frames import TTSSpeakFrame
from pipecat.services.llm_service import FunctionCallParams
from googleapiclient.discovery import build
from loguru import logger
import base64
from email.message import EmailMessage
import json
from .auth import get_google_credentials

async def get_gmail_emails(params: FunctionCallParams):
    """Get the 2 most recent Gmail emails.
    
    Args:
        params: FunctionCallParams (no arguments needed)
        
    Returns:
        str: JSON string of 2 most recent emails
    """
    try:
        logger.info("🛠 TOOL CALL: get_gmail_emails() invoked")

        # Bot speaks immediately before checking inbox
        await params.llm.push_frame(TTSSpeakFrame("Let me check your inbox"))
        
        logger.info(f"📧 Fetching 2 most recent Gmail emails")
        
        # Get authenticated Gmail service
        creds = get_google_credentials()
        service = build('gmail', 'v1', credentials=creds)
        
        # Get message IDs (list() only returns IDs, not full emails)
        message_ids = service.users().messages().list(
            userId='me',
            maxResults=2
        ).execute().get('messages', [])
        
        # Extract snippet, subject, and from for each email
        emails_list = []
        for msg in message_ids:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata'
            ).execute()
            
            # Extract snippet, subject, and from
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
    """Send an email via Gmail.

    Expected arguments from the LLM (passed via params.arguments):
        to:      Recipient email address
        subject: Email subject line
        body:    Email body text
    """
    try:
        to = params.arguments.get("to", "")
        subject = params.arguments.get("subject", "")
        body = params.arguments.get("body", "")

        logger.info(f"🛠 TOOL CALL: send_gmail_email() invoked — to={to}, subject={subject}")

        await params.llm.push_frame(TTSSpeakFrame(f"Sending that email now, sir."))

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
