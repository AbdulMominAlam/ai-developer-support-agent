"""
Executes validated SQL queries on the PostgreSQL database.
"""

import psycopg
from psycopg.rows import dict_row

from config import DATABASE_URL


def execute_sql(sql: str) -> list[dict]:
    """Runs a read-only SQL query and returns the results."""

    # Connect to the Neon PostgreSQL database.
    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    ) as connection:

        # Execute the validated SQL query.
        with connection.cursor() as cursor:
            cursor.execute(sql)

            # Return all rows as dictionaries.
            return cursor.fetchall()