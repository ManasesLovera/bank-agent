import os.path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from constants import SCOPES, BANKS


# Optional date range filters for narrowing transaction queries
# Format: YYYY/MM/DD (e.g., "2024/01/01")
# Set to None to disable date filtering
date_after = None   # Fetch emails after this date (inclusive)
date_before = None  # Fetch emails before this date (inclusive)

def get_creds():
    creds = None
    # 1. Try loading existing token
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
                print("\nToken is invalid or expired. Please run 'python auth.py' to re-authenticate.")
                return None
        else:
            print("\nAuthentication token not found or invalid.")
            print("Please run 'python auth.py' to authenticate for the first time.")
            return None
        
        # Save the refreshed credentials
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

import json

def get_bank_notifications():
    creds = get_creds()
    if not creds:
        return
        
    notifications_data = [] # List to store our dictionaries

    try:
        service = build("gmail", "v1", credentials=creds)
        
        # Check if BANKS dictionary is configured
        if not BANKS:
            print("No banks configured. Please add bank email addresses to the BANKS dictionary.")
            return
        
        # Build query to filter by specific bank email addresses
        email_filters = " OR ".join([f"from:{email}" for email in BANKS.values()])
        query = f"({email_filters})"
        
        # Add optional date range filters
        if date_after:
            query += f" after:{date_after}"
        if date_before:
            query += f" before:{date_before}"
        
        results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No bank emails found.")
            return

        for m in messages:
            msg = service.users().messages().get(userId='me', id=m['id']).execute()
            headers = msg.get('payload', {}).get('headers', [])
            
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
            sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")
            date = next((header['value'] for header in headers if header['name'] == 'Date'), "No Date")

            # Create a dictionary for this notification
            entry = {
                "id": m['id'],
                "from": sender,
                "subject": subject,
                "date": date,
                "snippet": msg['snippet']
            }
            notifications_data.append(entry)
            print(f"Captured: {subject}")

        # Write the entire list to a file
        with open("notifications.json", "w", encoding="utf-8") as f:
            json.dump(notifications_data, f, indent=4, ensure_ascii=False)
        
        print(f"\nSuccessfully saved {len(notifications_data)} notifications to notifications.json")

    except HttpError as error:
        print(f"An error occurred: {error}")



def print_labels():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = get_creds()

  try:
    # Call the Gmail API
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
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")
