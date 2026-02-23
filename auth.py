import os
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from constants import SCOPES

def main():
    """Run the OAuth2 flow to generate token.json."""
    # Determine the environment and select the appropriate credentials file
    app_env = os.getenv("APP_ENV", "desktop").lower()
    
    if app_env == "web":
        creds_file = "credentials-web.json"
    else:
        creds_file = "credentials-desktop.json"

    # Check if the selected credentials file exists
    if not os.path.exists(creds_file):
        print(f"Error: '{creds_file}' not found.")
        print(f"Please ensure you have downloaded the correct credentials from Google Cloud Console.")
        print(f"Current APP_ENV: {app_env}")
        return

    print(f"Starting authentication flow using: {creds_file}...")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        
        # This will open your default browser
        creds = flow.run_local_server(port=0)

        # Save the credentials for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
        print("\nSuccessfully authenticated!")
        print(f"Token saved to 'token.json' using {app_env} credentials.")
        print("You can now run 'uv run main.py'.")
        
    except Exception as e:
        print(f"An error occurred during authentication: {e}")

if __name__ == "__main__":
    main()
