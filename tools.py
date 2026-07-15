import json
from pathlib import Path
from datetime import datetime   #used to record when ticket is created


# Get the project folder
PROJECT_ROOT = Path(__file__).resolve().parent

# JSON files that act as our database
ACCOUNTS_FILE = PROJECT_ROOT / "data" / "accounts.json"
TICKETS_FILE = PROJECT_ROOT / "data" / "tickets.json"


def lookup_account(account_id): 
    """
    Look up an account using its ID.
    """

    # Open the accounts database
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file: #open file, read JSON, convert to python dictionary
        accounts = json.load(file) #load file

    # Check whether the account exists
    if account_id in accounts:

        return {
            "success": True,
            "account_id": account_id,
            "account": accounts[account_id]
        }

    else:

        return {
            "success": False,
            "message": "Account not found."
        }


def create_ticket(account_id, category, description):
    """
    Create a new support ticket.
    """

    # Make sure the account exists first
    account = lookup_account(account_id)

    if account["success"] == False:
        return account

    # Open the tickets database
    with open(TICKETS_FILE, "r", encoding="utf-8") as file: #r is for read,
        tickets = json.load(file) #again open the file

    # Generate a ticket ID
    ticket_number = len(tickets) + 1
    ticket_id = f"TKT-{ticket_number:04d}" # d is decimal integer and 4 means atleast digits long

    # Create the ticket
    ticket = {
        "ticket_id": ticket_id,
        "account_id": account_id,
        "category": category,
        "description": description,
        "status": "Open",
        "created_at": datetime.now().isoformat()  #i put the date time format
    }

    # Add the ticket to the list
    tickets.append(ticket)

    # Save the updated list
    with open(TICKETS_FILE, "w", encoding="utf-8") as file: #w is for write
        json.dump(tickets, file, indent=2) # python list gets converted to JSON and saved into tickets.json

    return {
        "success": True,
        "message": "Support ticket created successfully.",
        "ticket": ticket
    }