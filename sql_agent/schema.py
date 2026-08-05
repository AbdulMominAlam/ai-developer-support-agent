ALLOWED_SCHEMA = """
Database type: PostgreSQL

Table: developer_accounts
- account_id: varchar, primary key
- name: varchar
- email: varchar
- plan: varchar
- status: varchar
- monthly_api_calls_used: integer
- monthly_api_call_limit: integer

Table: support_tickets
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
    return ALLOWED_SCHEMA