from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP

# Allow imports from the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import project modules
from tools import lookup_account, create_ticket
from sql_agent.agent import run_sql_agent


# Create one MCP server that will expose all of our tools
mcp = FastMCP("Developer Support Server")


@mcp.tool()
def get_account(account_id: str) -> dict:
    """
    Look up a developer account using its account ID.

    Use this tool when the user asks about:
    - account details
    - subscription plan
    - account status
    - API usage
    """

    # Existing fixed SQL lookup.
    return lookup_account(account_id)


@mcp.tool()
def query_support_database(question: str) -> dict:
    """
    Answer questions about developer accounts and support tickets.

    Use this tool for:
    - account details
    - account plans
    - account status
    - API usage
    - support ticket history
    - ticket counts and summaries
    """

    # Send the user's question to the SQL agent.
    return run_sql_agent(question)


@mcp.tool()
def create_support_ticket(
    account_id: str,
    category: str,
    description: str,
) -> dict:
    """
    Create a support ticket for a developer account.

    Use this tool when the user asks to:
    - report a problem
    - create a support ticket
    - contact support
    """

    # Existing ticket creation logic.
    return create_ticket(
        account_id,
        category,
        description,
    )


# Start the MCP server only when this file is run directly.
if __name__ == "__main__":
    mcp.run()