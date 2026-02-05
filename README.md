# Bank Notification Agent

An intelligent financial assistant that "listens" to bank notification emails from your Gmail inbox and extracts structured transaction data (expenses, payroll, withdrawals) using LLMs.

## Project Overview

This agent automates the tracking of your personal finances by:
1. Monitoring emails from specific bank notification addresses (see `BANKS` dictionary in `gmailapi.py` for supported banks).
2. Fetching recent transaction emails via the **Gmail API**.
3. Processing the Spanish content with **Gemini 1.5 Flash** to output clean JSON.
4. Classifying the transaction and extracting amounts, merchants, and wallets.

---

## Google Cloud Setup

Before running the script, you must configure a Google Cloud Project to gain OAuth access to your Gmail.

### 1. Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `bank-agent`.
3. Search for **Gmail API** and click **Enable**.

### 2. Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **User Type: External** and click **Create**.
3. Fill in the **App Name** (e.g., "Bank Agent") and your **User support email**.
4. In the **Test users** section, click **Add Users** and enter your own Gmail address. 
   > **Note:** Without this step, you will receive a "403 Access Denied" error during login.

### 3. Create Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Select **Application type: Desktop app**.
4. Click **Create** and then **Download JSON**.
5. Rename the downloaded file to `credentials.json` and move it to your project root folder.

---

## Installation & Usage

### Option 1: Using `uv` (Recommended)
This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

```bash
# Initialize the environment and install dependencies
uv sync

# Run the project
uv run main.py
```

### Option 2: Using Plain Python & Pip

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-genai pydantic

# Run the project
python main.py
```

---

## Authentication
The first time you run the script:

1. A browser window will open asking you to sign in to your Google Account.
2. You will see a "Google hasn't verified this app" warning. Click Advanced > Go to [App Name] (unsafe).
3. Once authorized, a token.json file will be created in your folder. This file stores your login session so you don't have to log in manually again.

## Customizing Bank Filters

The application monitors emails from specific bank notification addresses. To add or remove banks, edit the `BANKS` dictionary in `gmailapi.py`:

```python
BANKS = {
    "Bank Name 1": "notifications@bank1.com",
    "Bank Name 2": "notifications@bank2.com",
    # Add more banks as needed
}
```

This approach ensures that only emails from these specific addresses are processed, avoiding false positives from other notification senders.

## Filtering by Date Range

You can optionally filter emails by date range using the `DATE_AFTER` and `DATE_BEFORE` constants in `gmailapi.py`:

```python
# Optional date range filters for narrowing transaction queries
# Format: YYYY/MM/DD (e.g., "2024/01/01")
# Set to None to disable date filtering
DATE_AFTER = "2024/01/01"   # Fetch emails after this date (inclusive)
DATE_BEFORE = "2024/12/31"  # Fetch emails before this date (inclusive)
```

**Examples:**
- To get all emails from 2024: Set `DATE_AFTER = "2024/01/01"` and `DATE_BEFORE = "2024/12/31"`
- To get emails from the last month: Set `DATE_AFTER = "2024/11/01"` and `DATE_BEFORE = "2024/11/30"`
- To get all emails after a specific date: Set `DATE_AFTER = "2024/06/01"` and `DATE_BEFORE = None`
- To disable date filtering: Set both `DATE_AFTER = None` and `DATE_BEFORE = None` (default)

## Project Structure

```plaintext
bank-agent/
├── credentials.json   # OAuth App ID (From Google Console)
├── token.json         # Your User Session (Generated after first login)
├── main.py            # Main application logic
├── pyproject.toml     # uv configuration & dependencies
└── README.md          # This file
``` 
