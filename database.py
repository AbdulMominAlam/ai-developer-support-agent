import os

import psycopg
from dotenv import load_dotenv


# Load variables from the .env file.
load_dotenv()

# Read the Neon PostgreSQL connection string.
DATABASE_URL = os.getenv("DATABASE_URL")

# Stop the program early if DATABASE_URL is missing.
if not DATABASE_URL:
    raise ValueError("DATABASE_URL was not found in the .env file.")


def get_connection():
    """
    Create and return a connection to the Neon PostgreSQL database.
    """
    return psycopg.connect(DATABASE_URL)