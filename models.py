"""
Pydantic models for structured GenAI transaction responses.

These models define the schema used by Gemini 2.0 Flash Lite to return
structured transaction data extracted from bank notification emails.
Each transaction response contains a type classification and a flexible
schema dictionary holding the transaction-specific extracted fields.
"""

from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    """
    Structured response from the GenAI model for a single bank notification.

    Attributes:
        transaction_type: The classification of the transaction
            (e.g., "expense", "payroll", "withdrawal", "transfer", "deposit").
        transaction_schema: A dictionary containing the extracted fields
            from the transaction. Keys and values vary by transaction type.
            Examples of common fields:
            - "amount": The monetary value of the transaction.
            - "currency": The currency code (e.g., "DOP", "USD").
            - "merchant": The name of the merchant or recipient.
            - "date": The date of the transaction.
            - "card_last_digits": Last digits of the card used.
            - "balance": Remaining balance after the transaction.
    """
    transaction_type: str = Field(
        description="The type of transaction: expense, payroll, withdrawal, transfer, deposit, or other."
    )
    transaction_schema: dict = Field(
        description="Extracted transaction details as key-value pairs. Fields vary by transaction type."
    )
