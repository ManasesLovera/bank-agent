"""
Gmail service for fetching and processing bank notification emails.

This module handles:
1. Authentication with the Gmail API using OAuth2 credentials.
2. Fetching bank notification emails filtered by configured bank addresses.
3. Processing each notification through the GenAI pipeline to extract
   structured transaction data.
4. Saving raw and extracted data to notifications.json.
"""

import json
import os.path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from constants import SCOPES, BANKS
from services.genai import extract_transaction


# Optional date range filters for narrowing transaction queries.
# Format: YYYY/MM/DD (e.g., "2024/01/01")
# Set to None to disable date filtering.
date_after = None   # Fetch emails after this date (inclusive)
date_before = None  # Fetch emails before this date (inclusive)


def get_creds() -> Credentials | None:
    """
    Load and return valid Gmail API credentials.

    Attempts to load credentials from token.json. If the token is expired,
    it will try to refresh it automatically. If no valid credentials are
    available, the user is prompted to run the auth.py script.

    Returns:
        Credentials: Valid OAuth2 credentials for the Gmail API,
            or None if authentication fails.
    """
    creds = None

    # 1. Try loading existing token from disk
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2. If token is missing or invalid, try to refresh it
    if not creds or not creds.valid:
        if creds and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print(
                    "\nToken is invalid or expired. "
                    "Please run 'python auth.py' to re-authenticate."
                )
                return None
        else:
            print("\nAuthentication token not found or invalid.")
            print("Please run 'python auth.py' to authenticate for the first time.")
            return None

        # Save the refreshed credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def _build_query() -> str:
    """
    Build the Gmail search query string for bank notification emails.

    Combines bank email address filters with optional date range filters
    to create a Gmail-compatible search query.

    Returns:
        str: A Gmail search query string.
    """
    # Filter by configured bank email addresses using OR logic
    email_filters = " OR ".join([f"from:{email}" for email in BANKS.values()])
    query = f"({email_filters})"

    # Append optional date range filters
    if date_after:
        query += f" after:{date_after}"
    if date_before:
        query += f" before:{date_before}"

    return query


def _extract_header(headers: list[dict], name: str, default: str = "") -> str:
    """
    Extract a specific header value from a list of email headers.

    Args:
        headers: List of header dictionaries with 'name' and 'value' keys.
        name: The header name to search for (e.g., 'Subject', 'From').
        default: Default value if the header is not found.

    Returns:
        str: The header value, or the default if not found.
    """
    return next(
        (header["value"] for header in headers if header["name"] == name),
        default,
    )


def get_bank_notifications() -> list[dict]:
    """
    Fetch bank notification emails and process them through the GenAI pipeline.

    This function:
    1. Authenticates with the Gmail API.
    2. Queries for bank notification emails using configured filters.
    3. Extracts email metadata (subject, sender, date, snippet).
    4. Processes each notification through Gemini 2.0 Flash Lite to extract
       structured transaction data.
    5. Saves the combined raw + extracted data to notifications.json.

    Returns:
        list[dict]: A list of notification dictionaries, each containing
            raw email data and an "extracted_data" field with the GenAI
            structured output (transaction_type and transaction_schema).
    """
    creds = get_creds()
    if not creds:
        return []

    # List to accumulate notification entries
    notifications_data = []

    try:
        # Build the Gmail API client
        service = build("gmail", "v1", credentials=creds)

        # Verify that banks are configured
        if not BANKS:
            print("No banks configured. Please add bank email addresses to BANKS in constants.py.")
            return []

        # Build and execute the search query
        query = _build_query()
        results = service.users().messages().list(
            userId="me", q=query, maxResults=5
        ).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No bank emails found.")
            return []

        print(f"Found {len(messages)} bank notification(s). Processing...\n")

        # Process each email message
        for m in messages:
            msg = service.users().messages().get(userId="me", id=m["id"]).execute()
            headers = msg.get("payload", {}).get("headers", [])

            # Extract email metadata from headers
            subject = _extract_header(headers, "Subject", "No Subject")
            sender = _extract_header(headers, "From", "Unknown Sender")
            date = _extract_header(headers, "Date", "No Date")
            snippet = msg.get("snippet", "")

            print(f"  Processing: {subject}")

            # Build the base notification entry with raw data
            entry = {
                "id": m["id"],
                "from": sender,
                "subject": subject,
                "date": date,
                "snippet": snippet,
                "extracted_data": None,
            }

            # Run the notification snippet through GenAI to extract transaction data
            result = extract_transaction(snippet)
            if result:
                entry["extracted_data"] = result.model_dump()
                print(f"    -> Type: {result.transaction_type}")
            else:
                print("    -> GenAI extraction failed, storing raw data only.")

            notifications_data.append(entry)

        # Write all notifications (raw + extracted) to disk
        with open("notifications.json", "w", encoding="utf-8") as f:
            json.dump(notifications_data, f, indent=4, ensure_ascii=False)

        print(f"\nSaved {len(notifications_data)} notifications to notifications.json")

    except HttpError as error:
        print(f"Gmail API error: {error}")

    return notifications_data


def print_labels() -> None:
    """
    Print all Gmail labels for the authenticated user.

    Useful for debugging and verifying Gmail API access.
    """
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
            print(f"  {label['name']}")

    except HttpError as error:
        print(f"Gmail API error: {error}")
