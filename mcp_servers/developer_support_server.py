from pathlib import Path
import sys
from sql_agent.agent import run_sql_agent
from mcp.server.fastmcp import FastMCP


# Allow imports from the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the Python functions we already created
from tools import lookup_account, create_ticket


# Create one MCP server that will expose all of our tools
mcp = FastMCP("Developer Support Server")


@mcp.tool()
def query_support_database(question: str) -> dict:
    """
    Answer questions about developer accounts and support tickets.

    Use this tool for:
    - account details
    - account plans and status
    - API usage
    - support ticket history
    - ticket counts and summaries
    """

    # Send the natural-language question to the SQL agent.
    return run_sql_agent(question)


@mcp.tool()
def create_support_ticket(
    account_id: str, #tells MCP that inputs are going to be string
    category: str,
    description: str,
) -> dict: #will return a dictionary
    """
    Create a support ticket for a developer account.
    
    Use this tool when the user asks to:
    - report a problem
    - create a support ticket
    - contact support
    """

    # Call our existing Python function
    return create_ticket(
        account_id,
        category,
        description,
    )


# Start the MCP server only when this file is run directly.
# Do not start it when another file imports it.
if __name__ == "__main__":
    mcp.run()