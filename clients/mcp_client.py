from pathlib import Path
import sys
import json

from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Get the main project folder.
# This file is inside clients/, so parent.parent moves
# back to the developer-support-agent folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add the project root to Python's import path.
sys.path.append(str(PROJECT_ROOT))


async def call_mcp_tool(tool_name, arguments):
    """
    Connect to the Developer Support MCP server,
    call the requested tool, and return its result.

    This function is asynchronous because communicating
    with the MCP server may take time.
    """

    # AsyncExitStack manages all resources that must be closed,
    # such as the MCP session, stdio connection, and server process.
    exit_stack = AsyncExitStack()

    try:
        # Tell the MCP client how to start our custom server.
        #
        # sys.executable uses the same Python interpreter
        # and virtual environment that is currently running this file.
        server = StdioServerParameters(
            command=sys.executable,
            args=[
                str(
                    PROJECT_ROOT
                    / "mcp_servers"
                    / "developer_support_server.py"
                )
            ],
        )

        # Start the MCP server and create a stdio connection.
        #
        # stdio allows the client and server to communicate
        # through standard input and standard output.
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server)
        )

        # Separate the connection into:
        # a stream for reading messages from the server
        # a stream for sending messages to the server
        read_stream, write_stream = stdio_transport

        # Create the MCP client session.
        # This session allows us to initialize the connection
        # and call tools exposed by the MCP server.
        session = await exit_stack.enter_async_context(
            ClientSession(
                read_stream,
                write_stream,
            )
        )

        # Complete the MCP handshake between client and server.
        await session.initialize()

        # Call whichever MCP tool was requested.
        #
        # Example tool names:
        # - get_account
        # - create_support_ticket
        result = await session.call_tool(
            tool_name,
            arguments,
        )

        # MCP returns tool output inside content objects.
        # We expect one response, so we take the first item.
        result_text = result.content[0].text

        # The server returns JSON text.
        # Convert it into a normal Python dictionary.
        result_dictionary = json.loads(result_text)

        return result_dictionary

    finally:
        # Close the session, stdio connection,
        # and MCP server process even if an error occurs.
        await exit_stack.aclose()


async def test_client():
    """
    Test both tools through the reusable MCP client.
    """

    print("\nTesting get_account...\n")

    account_result = await call_mcp_tool(
        "get_account",
        {
            "account_id": "ACC-1001"
        },
    )

    print(account_result)

    print("\nTesting query_support_database...\n")

    query_result = await call_mcp_tool(
        "query_support_database",
        {
            "question": "How many support tickets does account ACC-1001 have?"
        },
    )

    print(query_result)

    print("\nTesting create_support_ticket...\n")

    ticket_result = await call_mcp_tool(
        "create_support_ticket",
        {
            "account_id": "ACC-1001",
            "category": "Database issue",
            "description": "The database connection keeps failing.",
        },
    )

    print(ticket_result)


# Only run this test when this file is executed directly.
# Do not run it when agent.py imports call_mcp_tool().
if __name__ == "__main__":
    import asyncio

    asyncio.run(test_client())