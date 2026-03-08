import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
    credentials_file = os.environ.get("GMAIL_CREDENTIALS_FILE", "gmail_credentials.json")
    token_file = os.environ.get("GMAIL_TOKEN_FILE", "gmail_token.json")

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Missing {credentials_file}. Download OAuth client JSON from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    print(f"Gmail API authorization successful. Token saved to {token_file}")


if __name__ == "__main__":
    main()
