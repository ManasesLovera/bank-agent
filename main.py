"""
Bank Notification Agent - Main Entry Point

This script orchestrates the bank notification processing pipeline:
1. Fetches bank notification emails from Gmail using OAuth2 credentials.
2. Processes each notification through Gemini 2.0 Flash Lite to extract
   structured transaction data (type, amount, merchant, etc.).
3. Saves the combined raw and extracted data to notifications.json.
"""

from services.gmail import get_bank_notifications


def main():
    """
    Run the bank notification agent pipeline.

    Fetches bank notifications from Gmail and processes them through
    the GenAI pipeline to extract structured transaction data.
    Results are saved to notifications.json.
    """
    print("Bank Notification Agent")
    print("=" * 40)
    print()

    # Execute the full pipeline: fetch emails -> extract data -> save results
    notifications = get_bank_notifications()

    if notifications:
        print(f"\nPipeline complete. Processed {len(notifications)} notification(s).")
    else:
        print("\nNo notifications were processed.")


if __name__ == "__main__":
    main()
