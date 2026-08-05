"""
Stores the database schema that the SQL agent can use.

The schema is included in the prompt so the LLM knows
which tables and columns exist when generating SQL.
"""

# Schema available to the SQL agent.
ALLOWED_SCHEMA = """
Database type: PostgreSQL

Table: accounts
- account_id: varchar, primary key
- name: varchar
- email: varchar
- plan: varchar
- status: varchar
- monthly_api_calls_used: integer
- monthly_api_call_limit: integer

Table: tickets
- ticket_id: varchar, primary key
- account_id: varchar, foreign key
- category: varchar
- description: text
- status: varchar
- created_at: timestamp

Relationship:
support_tickets.account_id references developer_accounts.account_id
"""


def get_allowed_schema() -> str:
    """Returns the database schema for the SQL agent."""
    return ALLOWED_SCHEMA