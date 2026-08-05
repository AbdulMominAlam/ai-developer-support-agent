from pathlib import Path
import os

from dotenv import load_dotenv

# Absolute path to the main project folder.
BASE_DIR = Path(__file__).resolve().parent

# Load variables from the .env file.
load_dotenv(BASE_DIR / ".env")

API_TOKEN = os.getenv("API_TOKEN")  # Your personal API token.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.4-mini")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small",
)

DOCUMENTS_DIR = BASE_DIR / "documents"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "supabase_docs"

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from the .env file.")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from the .env file.")