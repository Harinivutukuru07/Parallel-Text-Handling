import base64
import mimetypes
import os
import time
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
MAX_GMAIL_ATTACHMENT_BYTES = 24 * 1024 * 1024


def _get_gmail_service():
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
                    f"Gmail API credentials file not found: {credentials_file}. "
                    "Download OAuth client JSON from Google Cloud Console and save it as gmail_credentials.json"
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    # Use a longer HTTP timeout for large payload uploads.
    http = httplib2.Http(timeout=180)
    authed_http = AuthorizedHttp(creds, http=http)
    return build("gmail", "v1", http=authed_http, cache_discovery=False)


def _validate_total_attachment_size(attachments):
    if not attachments:
        return

    total_bytes = 0
    for path, _ in attachments:
        if os.path.exists(path):
            total_bytes += os.path.getsize(path)

    if total_bytes > MAX_GMAIL_ATTACHMENT_BYTES:
        size_mb = total_bytes / (1024 * 1024)
        limit_mb = MAX_GMAIL_ATTACHMENT_BYTES / (1024 * 1024)
        raise ValueError(
            f"Attachments are too large ({size_mb:.2f} MB). Gmail limit is about {limit_mb:.0f} MB. "
            "Please send a smaller CSV sample."
        )


def send_email(receiver, total, positives, negatives, neutrals, processing_time, attachments=None):
    sender = os.environ.get("EMAIL_SENDER", "me")

    msg = EmailMessage()
    msg["Subject"] = "Sentiment Analysis Results"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(
        f"""Sentiment Analysis Completed

Total Reviews: {total}
Positive: {positives}
Negative: {negatives}
Neutral: {neutrals}

Processing Time: {processing_time} seconds
"""
    )

    _validate_total_attachment_size(attachments)

    if attachments:
        for path, name in attachments:
            with open(path, "rb") as file_obj:
                content = file_obj.read()
            content_type, _ = mimetypes.guess_type(path)
            if content_type:
                maintype, subtype = content_type.split("/", 1)
            else:
                maintype, subtype = "application", "octet-stream"
            msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=name)

    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service = _get_gmail_service()
    last_error = None

    # Retry transient network/API failures with exponential backoff.
    for attempt in range(1, 4):
        try:
            response = service.users().messages().send(
                userId="me",
                body={"raw": encoded_message},
            ).execute()
            return response
        except (TimeoutError, OSError, httplib2.HttpLib2Error, HttpError) as exc:
            last_error = exc
            if attempt == 3:
                break
            time.sleep(2 ** (attempt - 1))

    raise RuntimeError(f"Gmail API send failed after retries: {last_error}")