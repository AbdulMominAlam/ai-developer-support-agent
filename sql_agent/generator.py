"""
Generates a SQL query from the user's natural-language question.
"""

from openai import OpenAI

from config import MODEL_NAME
from sql_agent.prompts import SQL_GENERATION_PROMPT

# OpenAI client used to call the Responses API.
client = OpenAI()


def generate_sql(question: str, schema: str) -> str:
    """Uses GPT to generate a SQL query."""

    # Insert the database schema and user's question into the prompt.
    prompt = SQL_GENERATION_PROMPT.format(
        schema=schema,
        question=question,
    )

    # Send the prompt to GPT.
    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
    )

    # Return only the generated SQL query.
    return response.output_text.strip()