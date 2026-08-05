"""
Runs the complete SQL agent pipeline.
"""

from sql_agent.schema import get_allowed_schema
from sql_agent.generator import generate_sql
from sql_agent.validator import validate_sql
from sql_agent.executor import execute_sql


def run_sql_agent(question: str) -> dict:
    """Generate, validate, and execute SQL for a user question."""

    # Load the database schema for the prompt.
    schema = get_allowed_schema()

    # Ask GPT to generate SQL from the user's question.
    generated_sql = generate_sql(
        question=question,
        schema=schema,
    )

    # Check that the SQL is safe before executing it.
    validated_sql = validate_sql(generated_sql)

    # Run the validated query on PostgreSQL.
    rows = execute_sql(validated_sql)

    # Return structured output for the main OpenAI agent.
    return {
        "question": question,
        "sql": validated_sql,
        "rows": rows,
        "row_count": len(rows),
    }