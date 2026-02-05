import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Bank-specific email addresses for filtering transaction notifications
BANKS = {
    "Banco Popular": "notificaciones@popularenlinea.com",
    "Banesco": "notificaciones@banesco.com.do",
    "AZUL": "notificaciones@azul.com.do",  # This is the platform UAPA where I study uses for payments
    "Qik": "notificaciones@qik.do",
    "Lafise": "notificacioneslafisedo@lafise.com.do"
}

def get_creds():
    creds = None
    # 1. Try loading existing token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2. If token is missing or invalid, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # 3. CRITICAL: This must be at the top level of the function!
    return creds
  
import json

def get_bank_notifications():
    creds = get_creds()
    notifications_data = [] # List to store our dictionaries

    try:
        service = build("gmail", "v1", credentials=creds)
        # Build query to filter by specific bank email addresses
        email_filters = " OR ".join([f"from:{email}" for email in BANKS.values()])
        query = f"({email_filters})"
        results = service.users().messages().list(userId='me', q=query, maxResults=100).execute()
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
