import json

from database import get_connection


def import_accounts():
    with open("data/accounts.json", "r") as f:
        accounts = json.load(f)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            for account_id, account in accounts.items():

                cursor.execute(
                    """
                    INSERT INTO accounts (
                        account_id,
                        name,
                        email,
                        plan,
                        status,
                        monthly_api_calls_used,
                        monthly_api_call_limit
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (account_id) DO NOTHING;
                    """,
                    (
                        account_id,
                        account["name"],
                        account["email"],
                        account["plan"],
                        account["status"],
                        account["monthly_api_calls_used"],
                        account["monthly_api_call_limit"],
                    ),
                )

        connection.commit()

    print("Accounts imported successfully!")


def import_tickets():
    with open("data/tickets.json", "r") as f:
        tickets = json.load(f)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            for ticket in tickets:

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
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticket_id) DO NOTHING;
                    """,
                    (
                        ticket["ticket_id"],
                        ticket["account_id"],
                        ticket["category"],
                        ticket["description"],
                        ticket["status"],
                        ticket["created_at"],
                    ),
                )

        connection.commit()

    print("Tickets imported successfully!")


if __name__ == "__main__":
    import_accounts()
    import_tickets()    