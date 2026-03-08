import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv(override=True)
# Google API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
]

def get_google_credentials():
    """Get authenticated Google credentials for Calendar and Gmail APIs.
    
    Returns:
        Credentials: Authenticated Google OAuth2 credentials
    """
    creds = None
    CONFIG_PATH = os.getenv("CONFIG_PATH")
    credentials_path = CONFIG_PATH + "/credentials.json"
    token_path = CONFIG_PATH + "/token.json"

    # Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Google credentials file not found at {credentials_path}. "
                    "Please set GOOGLE_CREDENTIALS_PATH in your .env file or place credentials.json in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds
