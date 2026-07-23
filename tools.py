from database import get_connection


def lookup_account(account_id: str) -> dict:
    """
    Look up an account using its account ID.
    """     

    # Connect to the PostgreSQL database
    with get_connection() as connection:

        # Create a cursor to execute SQL queries
        with connection.cursor() as cursor:

            # Search for the account with the given account ID
            cursor.execute(
                """
                SELECT
                    account_id,
                    name,
                    email,
                    plan,
                    status,
                    monthly_api_calls_used,
                    monthly_api_call_limit
                FROM accounts
                WHERE account_id = %s;
                """,
                (account_id,),   # Value that replaces %s
            )

            # Fetch one matching row from the database
            account = cursor.fetchone()

    # If no account was found
    if account is None:
        return {
            "success": False,
            "message": "Account not found."
        }

    # Return the account details
    return {
        "success": True,
        "account_id": account[0],
        "account": {
            "name": account[1],
            "email": account[2],
            "plan": account[3],
            "status": account[4],
            "monthly_api_calls_used": account[5],
            "monthly_api_call_limit": account[6],
        }
    }


def create_ticket(account_id: str, category: str, description: str) -> dict:
    """
    Create a new support ticket.
    """

    # Make sure the account exists first
    account = lookup_account(account_id)

    if account["success"] == False:
        return account

    # Connect to PostgreSQL
    with get_connection() as connection:

        # Create a cursor for SQL queries
        with connection.cursor() as cursor:

            # Find the largest ticket number currently in the database
            cursor.execute(
                """
                SELECT COALESCE(
                    MAX(
                        CAST(
                            SUBSTRING(ticket_id FROM 5)
                            AS INTEGER
                        )
                    ),
                    0
                )
                FROM tickets;
                """
            )

            # Get the latest ticket number
            latest_ticket_number = cursor.fetchone()[0]

            # Generate the next ticket ID
            new_ticket_number = latest_ticket_number + 1
            ticket_id = f"TKT-{new_ticket_number:04d}"

            # Insert the new ticket into PostgreSQL
            cursor.execute(
                """
                INSERT INTO tickets (
                    ticket_id,
                    account_id,
                    category,
                    description,
                    status,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING
                    ticket_id,
                    account_id,
                    category,
                    description,
                    status,
                    created_at;
                """,
                (
                    ticket_id,
                    account_id,
                    category,
                    description,
                    "Open",
                ),
            )

            # Fetch the newly inserted ticket
            created_ticket = cursor.fetchone()

        # Save the changes permanently to the database
        connection.commit()

    # Convert the database row into a Python dictionary
    ticket = {
        "ticket_id": created_ticket[0],
        "account_id": created_ticket[1],
        "category": created_ticket[2],
        "description": created_ticket[3],
        "status": created_ticket[4],
        "created_at": created_ticket[5].isoformat(),
    }

    return {
        "success": True,
        "message": "Support ticket created successfully.",
        "ticket": ticket
    }