"""
Executes validated SQL queries on the PostgreSQL database.
"""

from psycopg.rows import dict_row

from database import get_connection


def execute_sql(sql: str) -> list[dict]:
    """Runs a read-only SQL query and returns the results."""

    # Reuse the project's existing Neon database connection.
    with get_connection() as connection:
        connection.row_factory = dict_row

        # Execute the validated query.
        with connection.cursor() as cursor:
            cursor.execute(sql)

            # Return the rows as dictionaries.
            return cursor.fetchall()