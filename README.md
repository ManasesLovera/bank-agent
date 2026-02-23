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

### 1. Initialize Environment

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

```bash
# Initialize the environment and install dependencies
uv sync
```

### 2. Authentication Setup

Before running the agent, you need to generate a `token.json` file for your Gmail account.

1. **Place Credentials:** Download your credentials from the Google Cloud Console and place them in the project root folder.

    * For **Desktop Application** credentials, rename the file to `credentials-desktop.json`.
    * For **Web Application** credentials, rename the file to `credentials-web.json`.

2. **Run Auth Script:** Execute the authentication script. By default, it looks for `credentials-desktop.json`. To use the web version, set the `APP_ENV` environment variable:

    ```bash
        # For Desktop (Default)
        python auth.py

        # For Web
        APP_ENV=web python auth.py
    ```

3. **Verify Token:** This script will open your browser for OAuth2 authorization. Once completed, a `token.json` file will be generated in your root folder.

### 3. Run the Project

Once authenticated, you can run the main application logic:

```bash
uv run main.py
```

---

## Configuration

### Customizing Bank Filters

The application monitors emails from specific bank notification addresses. To add or remove banks, edit the `BANKS` dictionary in `constants.py`:

```python
BANKS = {
    "Bank Name 1": "notifications@bank1.com",
    "Bank Name 2": "notifications@bank2.com",
    # Add more banks as needed
}
```

### Filtering by Date Range

You can optionally filter emails by date range using the `date_after` and `date_before` variables in `gmail.py`:

```python
# Format: YYYY/MM/DD (e.g., "2024/01/01")
date_after = "2024/01/01"   # Fetch emails after this date (inclusive)
date_before = "2024/12/31"  # Fetch emails before this date (inclusive)
```

---

## Project Structure

```plaintext
bank-agent/
├── auth.py                  # OAuth2 flow for initial authentication
├── constants.py             # Configuration for Scopes and Bank email addresses
├── credentials-desktop.json # OAuth App ID for Desktop (From Google Console)
├── credentials-web.json     # OAuth App ID for Web (From Google Console)
├── gmail.py                 # Logic for interacting with the Gmail API
├── main.py                  # Main application entry point
├── pyproject.toml           # uv configuration & dependencies
├── README.md                # Project documentation
├── services/
│   └── genai.py             # LLM processing logic (In Progress)
└── token.json               # Your User Session (Generated after auth.py)
```

---

## GenAI Processing (In Progress)

The integration of **Gemini 1.5 Flash** for extracting structured transaction data (amounts, merchants, wallets) from the email content is currently under development.
