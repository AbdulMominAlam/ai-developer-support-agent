"""
Tests the SQL agent directly from the terminal.
"""

from sql_agent.agent import run_sql_agent


question = input("Ask a database question: ")

result = run_sql_agent(question)

print("\nGenerated SQL:")
print(result["sql"])

print("\nRows:")
print(result["rows"])

print("\nRow count:")
print(result["row_count"])