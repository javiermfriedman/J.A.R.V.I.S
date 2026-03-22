import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv(override=True)

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
]


def _config_dir() -> Path:
    """Directory containing credentials.json and token.json (Google OAuth)."""
    env = os.getenv("CONFIG_PATH")
    if env:
        return Path(env).expanduser().resolve()
    # Default: this package's config/ (next to auth.py)
    # Default: this package's config/ (next to auth.py)
    return Path(__file__).resolve().parent / "config"


def get_google_credentials():
    """Get authenticated Google credentials for Calendar and Gmail APIs.
    
    Returns:
        Credentials: Authenticated Google OAuth2 credentials
    """
    creds = None
    config_dir = _config_dir()
    credentials_path = config_dir / "credentials.json"
    token_path = config_dir / "token.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found at {credentials_path}. "
                    "Set CONFIG_PATH to the directory containing credentials.json, "
                    "or place credentials.json in app/integrations/google/config/."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds
