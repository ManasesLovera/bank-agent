import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from constants import SCOPES

def main():
    """Run the OAuth2 flow to generate token.json."""
    if not os.path.exists("credentials.json"):
        print("Error: 'credentials.json' not found. Please download it from Google Cloud Console.")
        return

    print("Starting authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    
    # This will open your default browser
    creds = flow.run_local_server(port=0)

    # Save the credentials for next time
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    
    print("\nSuccessfully authenticated!")
    print("Token saved to 'token.json'. You can now run 'uv run main.py'.")

if __name__ == "__main__":
    main()
