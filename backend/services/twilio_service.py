from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

def send_message(message, to):
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
    msg = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_NUMBER"),
        to=to
    )
    
    # Fetch full status after sending
    result = client.messages(msg.sid).fetch()
    print(f"SID: {result.sid}")
    print(f"Status: {result.status}")
    print(f"Error Code: {result.error_code}")
    print(f"Error Message: {result.error_message}")
    return result

if __name__ == "__main__":
    send_message("Hello, world!", "+19175448054")