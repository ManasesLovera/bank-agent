import os.path
import json
import base64

from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from constants import SCOPES, BANKS


# Optional date range filters
date_after = None   # Format: "YYYY/MM/DD"
date_before = None


# ==============================
# AUTH
# ==============================

def get_creds():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print("Run: python auth.py")
                return None
        else:
            print("Authentication required. Run: python auth.py")
            return None

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


# ==============================
# BODY DECODING
# ==============================

def decode_body(data):
    if not data:
        return None

    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += "=" * (4 - missing_padding)

        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Body decode error: {e}")
        return None


# ==============================
# MIME EXTRACTION
# ==============================

def extract_preferred_body(payload):
    """
    Prefer text/plain.
    If not available, fallback to text/html.
    Recursively searches multipart structures.
    """
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")

    if mime_type == "text/plain" and body_data:
        return body_data, "text/plain"

    if mime_type == "text/html" and body_data:
        return body_data, "text/html"

    for part in payload.get("parts", []):
        data, mime = extract_preferred_body(part)
        if data:
            return data, mime

    return None, None


# ==============================
# HTML → TEXT PARSER
# ==============================

def html_to_text(html):
    """
    Convert HTML to clean structured text.
    Removes scripts/styles and normalizes whitespace.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Normalize whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


# ==============================
# MAIN FUNCTION
# ==============================

def get_bank_notifications():
    creds = get_creds()
    if not creds:
        return

    notifications_data = []

    try:
        service = build("gmail", "v1", credentials=creds)

        if not BANKS:
            print("No banks configured in BANKS dictionary.")
            return

        email_filters = " OR ".join([f"from:{email}" for email in BANKS.values()])
        query = f"({email_filters})"

        if date_after:
            query += f" after:{date_after}"
        if date_before:
            query += f" before:{date_before}"

        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=5
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            print("No bank emails found.")
            return

        for m in messages:
            msg: dict = service.users().messages().get(
                userId="me",
                id=m["id"]
            ).execute()

            headers = msg.get("payload", {}).get("headers", [])

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "No Date")

            payload = msg.get("payload", {})

            raw_body_data, mime_type = extract_preferred_body(payload)
            decoded_body = decode_body(raw_body_data)

            parsed_text = None

            if decoded_body:
                if mime_type == "text/html":
                    parsed_text = html_to_text(decoded_body)
                else:
                    parsed_text = decoded_body.strip()

            entry = {
                "id": m["id"],
                "threadId": msg.get("threadId"),
                "from": sender,
                "subject": subject,
                "date": date,
                "snippet": msg.get("snippet"),
                "body_raw": decoded_body,
                "body_text": parsed_text
            }

            notifications_data.append(entry)
            print(f"Captured: {subject}")

        with open("notifications.json", "w", encoding="utf-8") as f:
            json.dump(notifications_data, f, indent=4, ensure_ascii=False)

        print(f"\nSaved {len(notifications_data)} notifications to notifications.json")

    except HttpError as error:
        print(f"Gmail API error: {error}")


# ==============================
# LABEL DEBUGGING
# ==============================

def print_labels():
    creds = get_creds()
    if not creds:
        return

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return

        print("Labels:")
        for label in labels:
            print(label["name"])

    except HttpError as error:
        print(f"An error occurred: {error}")


# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    get_bank_notifications()
