from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP


# Allow imports from the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the Python functions we already created
from tools import lookup_account, create_ticket


# Create one MCP server that will expose all of our tools
mcp = FastMCP("Developer Support Server")


@mcp.tool()
def get_account(account_id: str) -> dict: #tells mcp that tool returns a dictionary and input must be string
    """
    Look up a developer account using its account ID.

    Use this tool when the user asks about:
    - account details
    - subscription plan
    - account status
    - API usage
    """

    # Call our existing Python function
    return lookup_account(account_id)


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