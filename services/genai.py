"""
GenAI service for extracting structured transaction data from bank notifications.

Uses the Gemini 2.0 Flash Lite model with structured output to classify
bank notification emails and extract transaction-specific fields into
a consistent JSON schema.
"""

import json

from google import genai
from google.genai import types

from config import settings
from models import TransactionResponse


# Gemini model identifier for transaction extraction
GEMINI_MODEL = "gemini-2.0-flash-lite"

# System prompt that instructs the model on how to process bank notifications
SYSTEM_PROMPT = """You are a financial data extraction assistant.
Your job is to analyze bank notification email text and extract structured transaction data.

For each notification, you must:
1. Classify the transaction type (expense, payroll, withdrawal, transfer, deposit, or other).
2. Extract all relevant fields from the text into a dictionary.

Common fields to extract (when present):
- amount: The monetary value of the transaction (as a number).
- currency: The currency code (e.g., "DOP", "USD").
- merchant: The name of the merchant, store, or recipient.
- date: The date/time of the transaction.
- card_last_digits: The last 4 digits of the card used.
- balance: The remaining balance after the transaction.
- reference_number: Any reference or confirmation number.
- account: Account number or identifier involved.
- description: Brief description of the transaction.

Only include fields that are clearly present in the notification text.
Return the data in the specified JSON schema."""


def get_genai_client() -> genai.Client:
    """
    Create and return a configured Gemini API client.

    Returns:
        genai.Client: An authenticated Gemini API client instance.

    Raises:
        ValueError: If GEMINI_API_KEY is not configured in settings.
    """
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Set GEMINI_API_KEY=your_key_here in your .env file."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def extract_transaction(notification_text: str) -> TransactionResponse | None:
    """
    Extract structured transaction data from a bank notification email snippet.

    Uses Gemini 2.0 Flash Lite with structured output to classify the
    transaction type and extract relevant fields from the email text.

    Args:
        notification_text: The raw text content (snippet) of the bank
            notification email to process.

    Returns:
        TransactionResponse: A structured response containing the transaction
            type and extracted schema fields, or None if extraction fails.
    """
    try:
        client = get_genai_client()

        # Call Gemini with structured output configuration
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"Extract transaction data from this bank notification:\n\n{notification_text}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=TransactionResponse,
            ),
        )

        # Parse the structured JSON response into our Pydantic model
        parsed = json.loads(response.text)
        return TransactionResponse(**parsed)

    except Exception as e:
        print(f"  [GenAI] Error extracting transaction data: {e}")
        return None
