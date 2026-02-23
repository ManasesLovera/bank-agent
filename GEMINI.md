# Gemini Project: Bank Notification Agent

## Project Overview

This project is an intelligent financial assistant that automates the tracking of personal finances by processing bank notification emails from a user's Gmail inbox. It leverages the Google Gmail API to fetch transaction emails and is designed to extract structured transaction data (expenses, payroll, withdrawals) using Large Language Models (LLMs), specifically Gemini 1.5 Flash (as inferred from the `README.md`).

Key technologies and components:

* **Python:** The primary programming language.
* **Google Gmail API:** Used to access and fetch bank notification emails.
* **Google OAuth2:** For secure authentication with Gmail.
* **Gemini 1.5 Flash (inferred):** For processing email content and extracting structured data.
* **`uv`:** A fast dependency manager for Python.
* **`pyproject.toml`:** Project configuration and dependency declaration.

## Building and Running

### Prerequisites: Google Cloud Setup

Before running the project, you must configure a Google Cloud Project with OAuth access to your Gmail. Refer to the original `README.md` for detailed steps on:

1. Creating a Google Cloud Project and enabling the Gmail API.
2. Configuring the OAuth Consent Screen (User Type: External, add your Gmail as a test user).
3. Creating OAuth client ID credentials (Desktop app type) and downloading `credentials.json` to the project root.

### Installation & Execution

The project uses `uv` for dependency management.

#### Option 1: Using `uv` (Recommended)

```bash
# Initialize the environment and install dependencies
uv sync

# Run the project
uv run main.py
```

#### Option 2: Using Plain Python & Pip

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-genai pydantic

# Run the project
python main.py
```

### Authentication

The first time you run the script, a browser window will open for Google account sign-in and OAuth authorization. A `token.json` file will be created to store your session for subsequent runs.

## Development Conventions

* **Dependency Management:** The project utilizes `uv` for efficient dependency management, with `pyproject.toml` defining the project's metadata and dependencies.
* **Google API Integration:** Follows standard practices for integrating with Google APIs, including OAuth2 for authentication and `google-api-python-client` for interacting with the Gmail API.
* **Project Structure:**
  * `main.py`: Entry point and main application logic.
  * `gmailapi.py`: Encapsulates Gmail API interactions, including authentication and email fetching.
  * `credentials.json`: OAuth App ID file from Google Cloud.
  * `token.json`: User session token (generated after first login).
  * `pyproject.toml`: Project configuration and dependencies.
  * `README.md`: Project documentation.

## Markdown Standards

When adjusting or creating `.md` files, follow these rules:

* **Rule:** `MD030` (list-marker-space)
* **Description:** Enforce a single space after list markers (e.g., `*`, `-`, `1.`).
* **Expected:** 1 space.
* **Actual Violation Example:** `1.  Item` (2 spaces).
* **Action:** Always use exactly one space after list markers.
