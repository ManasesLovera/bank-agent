# Bank Notification Agent

An intelligent financial assistant that "listens" to bank notification emails from your Gmail inbox and extracts structured transaction data (expenses, payroll, withdrawals) using LLMs.

## Project Overview

This agent automates the tracking of your personal finances by:

1. Monitoring emails from specific bank notification addresses (see `BANKS` dictionary in `constants.py` for supported banks).
2. Fetching recent transaction emails via the **Gmail API**.
3. Processing the email content with **Gemini 2.0 Flash Lite** using structured output to return clean JSON.
4. Classifying the transaction type and extracting amounts, merchants, wallets, and other relevant fields.
5. Storing both raw email data and extracted transaction data in `notifications.json`.

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

### 4. Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.
2. Copy the key and add it to your `.env` file as `GEMINI_API_KEY=your_key_here`.

---

## Installation & Usage

### 1. Initialize Environment

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.

```bash
# Initialize the environment and install dependencies
uv sync
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp dot.env .env
```

Edit `.env` and set your `GEMINI_API_KEY`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./test.db
```

### 3. Authentication Setup

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

### 4. Run the Project

Once authenticated, you can run the main application logic:

```bash
uv run main.py
```

---

## Pipeline Architecture

The agent processes bank notifications through a sequential pipeline:

```
Gmail Inbox
    │
    ▼
┌─────────────────────┐
│  Gmail API Service   │  Fetch emails filtered by bank sender addresses
│  (services/gmail.py) │  Extract metadata: subject, sender, date, snippet
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  GenAI Service       │  Process each snippet with Gemini 2.0 Flash Lite
│  (services/genai.py) │  Structured output: transaction_type + transaction_schema
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  notifications.json  │  Store raw email data + extracted transaction data
└─────────────────────┘
```

### GenAI Structured Output

Each notification is processed through **Gemini 2.0 Flash Lite** using structured output with a return schema. The response follows this format:

```json
{
    "transaction_type": "expense",
    "transaction_schema": {
        "amount": 1500.00,
        "currency": "DOP",
        "merchant": "Supermercado Nacional",
        "date": "2024-03-15",
        "card_last_digits": "1234",
        "balance": 25000.50
    }
}
```

### notifications.json Format

Each entry in `notifications.json` contains both the raw email data and the extracted transaction data:

```json
[
    {
        "id": "abc123",
        "from": "notificaciones@bank.com",
        "subject": "Transaction Alert",
        "date": "Mon, 15 Mar 2024 10:30:00 -0400",
        "snippet": "You spent DOP 1,500.00 at Supermercado Nacional...",
        "extracted_data": {
            "transaction_type": "expense",
            "transaction_schema": {
                "amount": 1500.00,
                "currency": "DOP",
                "merchant": "Supermercado Nacional"
            }
        }
    }
]
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

You can optionally filter emails by date range using the `date_after` and `date_before` variables in `services/gmail.py`:

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
├── config.py                # Application settings (env variables via Pydantic)
├── constants.py             # Configuration for Scopes and Bank email addresses
├── credentials-desktop.json # OAuth App ID for Desktop (From Google Console)
├── credentials-web.json     # OAuth App ID for Web (From Google Console)
├── database.py              # SQLAlchemy database engine configuration
├── dot.env                  # Example environment file template
├── main.py                  # Main application entry point and pipeline orchestrator
├── models.py                # Pydantic models for GenAI structured output
├── pyproject.toml           # uv configuration & dependencies
├── README.md                # Project documentation
├── services/
│   ├── genai.py             # Gemini 2.0 Flash Lite integration for transaction extraction
│   └── gmail.py             # Gmail API service for fetching bank notifications
└── token.json               # Your User Session (Generated after auth.py)
```

---

## GenAI Processing

The integration of **Gemini 2.0 Flash Lite** extracts structured transaction data from bank notification email snippets. Key features:

- **Structured Output:** Uses `response_mime_type="application/json"` and a Pydantic `response_schema` to enforce consistent JSON responses.
- **Transaction Classification:** Each notification is classified into a type (expense, payroll, withdrawal, transfer, deposit, or other).
- **Flexible Schema:** The `transaction_schema` dictionary adapts to each transaction type, extracting only the fields present in the notification text.
- **Error Handling:** If GenAI extraction fails for a notification, the raw data is still saved with `extracted_data` set to `null`.
