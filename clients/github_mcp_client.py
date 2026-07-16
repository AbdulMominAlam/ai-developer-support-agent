from pathlib import Path
import asyncio
import json
import os

from contextlib import AsyncExitStack

from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Load environment variables from the .env file.
load_dotenv()


# Get the main project folder.
#
# This file is inside:
# clients/github_mcp_client.py
#
# parent.parent moves back to:
# developer-support-agent/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Path to the official GitHub MCP Server executable.
GITHUB_MCP_SERVER = (
    PROJECT_ROOT
    / "external_servers"
    / "github"
    / "github-mcp-server.exe"
)


def get_github_token():
    """
    Read and validate the GitHub personal access token.

    Returns:
        The GitHub token as a string.
    """

    github_token = os.getenv(
        "GITHUB_PERSONAL_ACCESS_TOKEN"
    )

    # Stop immediately if the token
    # was not found in the .env file.
    if not github_token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN was not found in .env"
        )

    return github_token


def create_server_parameters(github_token):
    """
    Create the settings used to start
    the official GitHub MCP Server.
    """

    # Copy all current environment variables.
    #
    # This keeps important Windows variables,
    # such as PATH, while allowing us to add
    # the GitHub token.
    server_environment = os.environ.copy()

    # Pass the GitHub token to the MCP server process.
    server_environment[
        "GITHUB_PERSONAL_ACCESS_TOKEN"
    ] = github_token

    return StdioServerParameters(
        # Start the downloaded GitHub MCP executable.
        command=str(GITHUB_MCP_SERVER),

        args=[
            # Use standard input and standard output
            # for communication with our Python client.
            "stdio",

            # Only expose the GitHub tool groups
            # needed by our project.
            "--toolsets=issues,repos,users",

            # Prevent tools that create, edit,
            # or delete GitHub data.
            "--read-only",
        ],

        # Environment variables passed to
        # the GitHub MCP Server process.
        env=server_environment,
    )


def parse_github_tool_result(result):
    """
    Convert a GitHub MCP tool result into
    a Python dictionary, list, or string.

    GitHub tools may return:
    - structured content
    - normal text
    - JSON text
    - embedded files or resources
    """

    # Some MCP tools return structured data
    # separately from the normal content list.
    structured_content = getattr(
        result,
        "structuredContent",
        None,
    )

    if structured_content is not None:
        return structured_content

    # Check whether the MCP server reported an error.
    if getattr(result, "isError", False):

        error_parts = []

        for content_item in result.content:

            # Normal text error message.
            if hasattr(content_item, "text"):
                error_parts.append(
                    content_item.text
                )

            # Embedded resource error information.
            elif (
                hasattr(content_item, "resource")
                and hasattr(content_item.resource, "text")
            ):
                error_parts.append(
                    content_item.resource.text
                )

        error_message = "\n".join(
            error_parts
        ).strip()

        return {
            "success": False,
            "message": (
                error_message
                or "The GitHub MCP tool returned an error."
            ),
        }

    # Store every useful piece of returned content.
    text_parts = []

    for content_item in result.content:

        # Normal MCP TextContent objects store
        # their text directly in:
        #
        # content_item.text
        if hasattr(content_item, "text"):
            text_parts.append(
                content_item.text
            )

        # GitHub file-reading tools may return
        # EmbeddedResource objects.
        #
        # Their actual file contents are stored in:
        #
        # content_item.resource.text
        elif (
            hasattr(content_item, "resource")
            and hasattr(content_item.resource, "text")
        ):
            text_parts.append(
                content_item.resource.text
            )

        # Fallback for an unexpected content type.
        #
        # This prevents the result from being
        # silently discarded.
        else:
            text_parts.append(
                str(content_item)
            )

    # Combine all returned text pieces.
    result_text = "\n".join(
        text_parts
    ).strip()

    # Return a clear response if the tool
    # unexpectedly returned nothing.
    if not result_text:
        return {
            "success": False,
            "message": (
                "The GitHub MCP tool returned no content."
            ),
        }

    # Many GitHub tools return JSON as text.
    # Convert the JSON text into Python data.
    try:
        return json.loads(
            result_text
        )

    # File contents and ordinary messages
    # are not always JSON, so return them
    # as normal text.
    except json.JSONDecodeError:
        return result_text


async def call_github_mcp_tool(
    tool_name,
    arguments,
):
    """
    Connect to the official GitHub MCP Server,
    call one GitHub tool, and return its result.

    Parameters:
        tool_name:
            The name of the GitHub MCP tool.

        arguments:
            A dictionary containing the arguments
            required by the selected tool.
    """

    # Read and validate the GitHub token.
    github_token = get_github_token()

    # Make sure the GitHub MCP executable exists
    # before trying to start it.
    if not GITHUB_MCP_SERVER.exists():
        raise FileNotFoundError(
            "GitHub MCP Server executable was not found at: "
            f"{GITHUB_MCP_SERVER}"
        )

    # Keeps track of all opened resources:
    # - GitHub MCP server process
    # - stdio connection
    # - MCP client session
    #
    # Everything is closed automatically
    # when this block finishes.
    async with AsyncExitStack() as exit_stack:

        # Create the settings used to start
        # the GitHub MCP Server.
        server = create_server_parameters(
            github_token
        )

        # Start the GitHub MCP Server and open
        # a stdio connection to it.
        #
        # stdin:
        # Our client sends requests to the server.
        #
        # stdout:
        # Our client receives responses from the server.
        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server)
        )

        # Separate the connection into:
        # - a stream for reading responses
        # - a stream for sending requests
        read_stream, write_stream = stdio_transport

        # Create the MCP client session.
        session = await exit_stack.enter_async_context(
            ClientSession(
                read_stream,
                write_stream,
            )
        )

        # Complete the MCP handshake.
        await session.initialize()

        # Call the selected GitHub MCP tool.
        result = await session.call_tool(
            tool_name,
            arguments,
        )

        # Convert the raw MCP result into
        # data that agent.py can use.
        return parse_github_tool_result(
            result
        )


async def list_github_tools():
    """
    Connect to the GitHub MCP Server and display
    the schemas for the three tools used by our agent.
    """

    github_token = get_github_token()

    async with AsyncExitStack() as exit_stack:

        server = create_server_parameters(
            github_token
        )

        stdio_transport = await exit_stack.enter_async_context(
            stdio_client(server)
        )

        read_stream, write_stream = stdio_transport

        session = await exit_stack.enter_async_context(
            ClientSession(
                read_stream,
                write_stream,
            )
        )

        await session.initialize()

        # Ask the GitHub MCP Server which
        # tools it currently exposes.
        tools_result = await session.list_tools()

        print("\nAvailable GitHub MCP Tools:\n")

        selected_tools = [
            "search_repositories",
            "list_issues",
            "get_file_contents",
        ]

        for tool in tools_result.tools:

            # Only display the three tools
            # exposed through our AI agent.
            if tool.name in selected_tools:

                print("=" * 60)
                print(
                    f"Tool name: {tool.name}"
                )

                print(
                    f"\nDescription:\n"
                    f"{tool.description}"
                )

                # inputSchema contains the exact
                # arguments accepted by the tool.
                print("\nInput schema:")

                print(
                    json.dumps(
                        tool.inputSchema,
                        indent=2,
                    )
                )

                print()


async def test_search_repositories():
    """
    Test GitHub repository search directly.
    """

    result = await call_github_mcp_tool(
        "search_repositories",
        {
            "query": "ai-developer-support-agent",
            "perPage": 5,
        },
    )

    print("\nRepository search result:\n")
    print(result)


async def test_list_issues():
    """
    Test listing open issues from a repository.
    """

    result = await call_github_mcp_tool(
        "list_issues",
        {
            "owner": "microsoft",
            "repo": "vscode",
            "state": "OPEN",
            "perPage": 5,
        },
    )

    print("\nIssue result:\n")
    print(result)


async def test_read_github_file():
    """
    Test reading README.md from the project's
    GitHub repository.
    """

    result = await call_github_mcp_tool(
        "get_file_contents",
        {
            "owner": "AbdulMominAlam",
            "repo": "ai-developer-support-agent",
            "path": "README.md",
        },
    )

    print("\nFile result:\n")
    print(result)


# Run one direct test only when this file
# is executed by itself.
#
# This section does not run when agent.py
# imports call_github_mcp_tool().
if __name__ == "__main__":
    asyncio.run(
        list_github_tools()
    )