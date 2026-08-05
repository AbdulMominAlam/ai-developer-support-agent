from openai import OpenAI

from config import MODEL_NAME
from sql_agent.prompts import SQL_GENERATION_PROMPT

client = OpenAI()


def generate_sql(question: str, schema: str) -> str:
    prompt = SQL_GENERATION_PROMPT.format(
        schema=schema,
        question=question,
    )

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
    )

    return response.output_text.strip()