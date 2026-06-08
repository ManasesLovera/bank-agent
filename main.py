from services.gmail import get_bank_notifications

def main():
    print("Hello from bank-agent!")
    get_bank_notifications()


if __name__ == "__main__":
    main()
