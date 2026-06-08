"""
Pydantic models for structured GenAI transaction responses.

These models define the schema used by Gemini 2.0 Flash Lite to return
structured transaction data extracted from bank notification emails.
Each transaction response contains a type classification and a flexible
schema dictionary holding the transaction-specific extracted fields.
"""

from pydantic import BaseModel, Field


class TransactionDetails(BaseModel):
    """
    Extracted transaction details. Keys are optional and only populated if found.
    """
    amount: float | None = Field(default=None, description="The monetary value of the transaction (as a number).")
    currency: str | None = Field(default=None, description="The currency code (e.g., 'DOP', 'USD').")
    merchant: str | None = Field(default=None, description="The name of the merchant, store, or recipient.")
    date: str | None = Field(default=None, description="The date/time of the transaction.")
    card_last_digits: str | None = Field(default=None, description="The last 4 digits of the card used.")
    balance: float | None = Field(default=None, description="The remaining balance after the transaction.")
    reference_number: str | None = Field(default=None, description="Any reference or confirmation number.")
    account: str | None = Field(default=None, description="Account number or identifier involved.")
    description: str | None = Field(default=None, description="Brief description of the transaction.")


class TransactionResponse(BaseModel):
    """
    Structured response from the GenAI model for a single bank notification.

    Attributes:
        transaction_type: The classification of the transaction
            (e.g., "expense", "payroll", "withdrawal", "transfer", "deposit").
        transaction_schema: A structured object containing the extracted fields
            from the transaction.
    """
    transaction_type: str = Field(
        description="The type of transaction: expense, payroll, withdrawal, transfer, deposit, or other."
    )
    transaction_schema: TransactionDetails = Field(
        description="Extracted transaction details as key-value pairs. Fields vary by transaction type."
    )
