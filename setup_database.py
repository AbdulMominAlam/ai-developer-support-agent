from database import get_connection


def create_tables():
    """
    Create all PostgreSQL tables required by the project.
    """

    # Connect to the Neon PostgreSQL database
    with get_connection() as connection:

        # Create a cursor so we can execute SQL commands
        with connection.cursor() as cursor:

            # Create the accounts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    plan VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    monthly_api_calls_used INTEGER NOT NULL DEFAULT 0,
                    monthly_api_call_limit INTEGER NOT NULL
                );
                """
            )

            # Create the tickets table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id VARCHAR(20) PRIMARY KEY,
                    account_id VARCHAR(20) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'Open',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_ticket_account
                        FOREIGN KEY (account_id)
                        REFERENCES accounts(account_id)
                        ON DELETE CASCADE
                );
                """
            )

            # Create the sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(100) PRIMARY KEY,
                    response_id TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        # Save the table creation changes
        connection.commit()

    print("All tables created successfully!")


if __name__ == "__main__":
    create_tables()