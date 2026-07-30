import asyncio
import json

from openai import AsyncOpenAI

from config import MODEL_NAME, OPENAI_API_KEY
from rag.answer import answer_question
from clients.mcp_client import call_mcp_tool
from clients.github_mcp_client import call_github_mcp_tool


# Create an asynchronous OpenAI client.
# We use AsyncOpenAI because the rest of our agent,
# MCP clients, and tool flow are asynchronous.
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)


# These instructions describe the agent's overall behaviour.
#
# We send these instructions with every GPT request because
# instructions are not automatically carried forward when
# using previous_response_id.
AGENT_INSTRUCTIONS = """
You are a developer support agent.

You can:
- Search official Supabase documentation.
- Look up developer account information.
- Create developer support tickets.
- Search GitHub for repositories.

Tool rules:
- Use search_documentation for Supabase documentation questions.
- Use get_account for account-specific information.
- Use create_support_ticket only when the user clearly asks to
  create, open, or submit a support ticket.
- Use search_github_repositories when the user wants to search
  GitHub for repositories or projects.
- Use list_github_issues when the user asks to view issues
  in a specific GitHub repository.
- Use read_github_file when the user asks to read a file
  or directory from a GitHub repository.
- Never invent account information, ticket information,
  documentation details, or GitHub repository results.
- Use information from earlier messages when the user says things
  such as "it", "that account", "the same account", or "for them".

Response rules:
- Give clear and concise answers.
- Do not mention internal Python code, JSON, MCP, or tool calls.
- Base tool-related answers only on the result returned by the tool.
- Do not offer additional help unless the user asks for it.
- Do not end responses with follow-up questions.
"""


# Tool definitions shown to GPT.
#
# GPT reads the tool names, descriptions, and parameters,
# then decides whether one of the tools is needed.
TOOLS = [
    {
        "type": "function",
        "name": "search_documentation",
        "description": (
            "Search the official Supabase documentation using RAG. "
            "Use this for questions about authentication, passwords, "
            "API keys, databases, the Data API, storage, or file limits."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "The Supabase documentation question to search."
                    ),
                }
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_account",
        "description": (
            "Look up a developer account. Use this when the user asks "
            "about an account's name, plan, status, monthly API usage, "
            "or API usage limit."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": (
                        "The account ID, such as ACC-1001."
                    ),
                }
            },
            "required": ["account_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_support_ticket",
        "description": (
            "Create a support ticket for a developer account. "
            "Use this only when the user clearly asks to report "
            "a problem or create a support ticket."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": (
                        "The account ID, such as ACC-1001."
                    ),
                },
                "category": {
                    "type": "string",
                    "description": (
                        "The general category of the support issue."
                    ),
                },
                "description": {
                    "type": "string",
                    "description": (
                        "A clear description of the user's problem."
                    ),
                },
            },
            "required": [
                "account_id",
                "category",
                "description",
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_github_repositories",
        "description": (
            "Search GitHub for repositories. "
            "Use this when the user asks to find a repository, "
            "search GitHub for projects, or look for repositories "
            "by name, description, or topic."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The GitHub repository search query, "
                        "such as 'AI developer support agent'."
                    ),
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_github_issues",
        "description": (
            "List issues from a GitHub repository. "
            "Use this when the user asks to see open or closed issues "
            "for a specific repository."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": (
                        "The GitHub username or organization "
                        "that owns the repository."
                    ),
                },
                "repo": {
                    "type": "string",
                    "description": "The repository name.",
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "OPEN",
                        "CLOSED",
                    ],
                    "description": (
                        "Optional issue state filter. "
                        "Use OPEN for open issues or CLOSED for closed issues."
                    ),
                },
            },
            "required": [
                "owner",
                "repo",
            ],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_github_file",
        "description": (
            "Read a file or directory from a GitHub repository. "
            "Use this when the user asks to view a README, source file, "
            "configuration file, or directory contents."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": (
                        "The GitHub username or organization "
                        "that owns the repository."
                    ),
                },
                "repo": {
                    "type": "string",
                    "description": "The repository name.",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "The path to the file or directory, "
                        "such as README.md or src/main.py."
                    ),
                },
            },
            "required": [
                "owner",
                "repo",
                "path",
            ],
            "additionalProperties": False,
        },
    },
]


async def run_tool(tool_name, arguments): #routing logic
    """
    Execute the tool selected by GPT.

    Documentation questions go through our RAG pipeline.

    Account lookup and ticket creation go through
    our custom Developer Support MCP Server.

    GitHub repository searches go through
    GitHub's official MCP Server.
    """

    if tool_name == "search_documentation":

        # answer_question() is currently a normal synchronous function.
        #
        # asyncio.to_thread() runs it in a separate thread so that
        # it does not block our asynchronous agent.
        return await asyncio.to_thread(
            answer_question,
            arguments["question"],
        )

    if tool_name == "get_account":

        # Call the get_account tool through
        # our custom Developer Support MCP Server.
        return await call_mcp_tool(
            "get_account",
            {
                "account_id": arguments["account_id"]
            },
        )

    if tool_name == "create_support_ticket":

        # Call the ticket creation tool through
        # our custom Developer Support MCP Server.
        return await call_mcp_tool(
            "create_support_ticket",
            {
                "account_id": arguments["account_id"],
                "category": arguments["category"],
                "description": arguments["description"],
            },
        )

    if tool_name == "search_github_repositories":

        # GPT knows this tool by the application-level name:
        #
        # search_github_repositories
        #
        # The official GitHub MCP Server exposes the tool as:
        #
        # search_repositories
        #
        # This block maps our tool name to GitHub's tool name.
        return await call_github_mcp_tool(
            "search_repositories", #this name we found when i listed all the tools
            {
                "query": arguments["query"],
            },
        )

    if tool_name == "list_github_issues":

        github_arguments = {
            "owner": arguments["owner"],
            "repo": arguments["repo"],
            "perPage": 10  #only return 10 issues and not all
        }

    # Only include state if GPT supplied it.
        if "state" in arguments:
            github_arguments["state"] = arguments["state"]

        return await call_github_mcp_tool(
            "list_issues",
            github_arguments,
        )


    if tool_name == "read_github_file":

        return await call_github_mcp_tool(
            "get_file_contents",
            {
                "owner": arguments["owner"],
                "repo": arguments["repo"],
                "path": arguments["path"],
            },
        )

    # Safety response in case GPT requests a tool
    # that does not exist in our application.
    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}",
    }



def convert_tool_result_to_text(tool_result):
    """
    Convert a tool result into text that can be sent to GPT.

    MCP tools usually return Python dictionaries or lists.
    The RAG function returns a normal string.
    """

    # RAG answers and some MCP outputs are already strings,
    # so no conversion is needed.
    if isinstance(tool_result, str):
        return tool_result

    # Convert dictionaries or lists into JSON text.
    return json.dumps(
        tool_result,
        indent=2,
    )


async def process_message(
    user_message,
    previous_response_id=None,
):
    """
    Process one message in the conversation.

    Parameters:
        user_message:
            The user's newest message.

        previous_response_id:
            The ID of GPT's previous response.

            Passing this ID lets GPT access the earlier
            conversation and understand follow up messages.

    Returns:
        A dictionary containing:
        - the final answer
        - the new response ID
        - the tool used, if any
    """

    # Build the information needed for the first GPT request.
    first_request = {
        "model": MODEL_NAME,
        "instructions": AGENT_INSTRUCTIONS,
        "input": user_message,
        "tools": TOOLS,
    }

    # If this is not the first message, connect this request
    # to the previous GPT response.
    # This gives the agent conversation memory.
    if previous_response_id is not None:
        first_request["previous_response_id"] = previous_response_id

    # First GPT call:
    
    # GPT reads:
    # the newest user message
    #  the previous conversation
    # all available tools
    
    # It then either:
    # - answers directly
    # - requests one or more tools
    first_response = await client.responses.create(
        **first_request
    )

    # The OpenAI SDK communicates with OpenAI over HTTPS.
    # We do not manually write GET or POST requests because
    # the SDK handles the network communication for us.

    # Store every function call requested by GPT.
    function_calls = [
        output_item
        for output_item in first_response.output
        if output_item.type == "function_call"
    ]

    # If GPT did not request a tool,
    # return its direct answer.
    if not function_calls:
        return {
            "type": "direct_answer",
            "answer": first_response.output_text,
            "tool": None,
            "response_id": first_response.id,
        }

    # This list will contain the results that must be
    # sent back to GPT after the tools have finished.
    tool_outputs = []

    # Keep track of tool names for testing and debugging.
    tools_used = []

    # Run every tool requested by GPT.
    for function_call in function_calls:

        # Name of the tool selected by GPT.
        tool_name = function_call.name

        # GPT provides the tool arguments as JSON text.
        # Convert them into a Python dictionary.
        arguments = json.loads(
            function_call.arguments
        )

        # Run the selected RAG, custom MCP,
        # or GitHub MCP tool.
        tool_result = await run_tool(
            tool_name,
            arguments,
        )

        # Convert the result into text before giving it to GPT.
        tool_result_text = convert_tool_result_to_text(
            tool_result
        )

        # GPT gave this tool call a unique call_id.
        # We must return the result using the same call_id
        # so GPT knows which tool call the result belongs to.
        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": tool_result_text,
            }
        )

        tools_used.append(tool_name)

    # Second GPT call:
    #
    # Send the tool results back to the exact response
    # that originally requested those tools.
    #
    # GPT then converts the raw tool data into a clear,
    # natural-language final answer.
    final_response = await client.responses.create(
        model=MODEL_NAME,
        instructions=AGENT_INSTRUCTIONS,
        previous_response_id=first_response.id,
        input=tool_outputs,
        tools=TOOLS,
    )

    return {
        "type": "tool_call",
        "answer": final_response.output_text,
        "tool": (
            tools_used[0]
            if len(tools_used) == 1
            else tools_used
        ),
        "response_id": final_response.id,
    }


async def process_message_stream_test(
    user_message,
):
    """
    Temporary OpenAI streaming test.

    This function sends the user's message directly to OpenAI
    without RAG, MCP tools, or PostgreSQL conversation memory.

    It yields small event dictionaries as OpenAI generates text.
    """

    # Create a streaming Responses API request.
    #
    # stream=True tells OpenAI not to wait for the complete answer.
    # Instead, OpenAI sends many events while generating.
    stream = await client.responses.create(
        model=MODEL_NAME,
        instructions=(
            "You are a concise developer support assistant."
        ),
        input=user_message,
        stream=True,
    )

    # Keep track of the OpenAI response ID.
    response_id = None

    # Read each streaming event as it arrives.
    async for event in stream:

        # OpenAI sends this event when the response is created.
        #
        # We save its ID so conversation memory can be added later.
        if event.type == "response.created":
            response_id = event.response.id

        # This event contains one small piece
        # of the generated answer.
        if event.type == "response.output_text.delta":
            yield {
                "type": "text_delta",
                "delta": event.delta,
            }

        # This event means OpenAI finished generating.
        if event.type == "response.completed":

            # Use the completed response ID as the final value.
            response_id = event.response.id

            yield {
                "type": "response_completed",
                "tool": None,
                "response_id": response_id,
            }