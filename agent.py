import asyncio
import json

from openai import AsyncOpenAI

from config import MODEL_NAME, OPENAI_API_KEY
from rag.answer import answer_question
from clients.mcp_client import call_mcp_tool


# Create an asynchronous OpenAI client.
#
# We use AsyncOpenAI instead of OpenAI because the rest
# of our agent and MCP flow is now asynchronous.
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

Tool rules:
- Use search_documentation for Supabase documentation questions.
- Use get_account for account-specific information.
- Use create_support_ticket only when the user clearly asks to
  create, open, or submit a support ticket.
- Never invent account information or ticket information.
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
]


async def run_tool(tool_name, arguments):
    """
    Execute the tool selected by GPT.

    Documentation questions go through our RAG pipeline.

    Account lookup and ticket creation go through:
        MCP client
        -> MCP server
        -> backend function
        -> JSON data
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
        return await call_mcp_tool(
            "get_account",
            {
                "account_id": arguments["account_id"]
            },
        )

    if tool_name == "create_support_ticket":
        return await call_mcp_tool(
            "create_support_ticket",
            {
                "account_id": arguments["account_id"],
                "category": arguments["category"],
                "description": arguments["description"],
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

    MCP tools return Python dictionaries.
    The RAG function returns a normal string.
    """

    # RAG answers are already strings,
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
            conversation and understand follow-up messages.

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
    #
    # This gives the agent conversation memory.
    if previous_response_id is not None:
        first_request["previous_response_id"] = previous_response_id

    # First GPT call:
    #
    # GPT reads the new message and previous conversation.
    # It then either:
    # - answers directly
    # - requests one of our tools
    first_response = await client.responses.create(
        **first_request
    )

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

        tool_name = function_call.name

        # GPT provides the tool arguments as JSON text.
        # Convert them into a Python dictionary.
        arguments = json.loads(
            function_call.arguments
        )

        # Run the selected RAG or MCP tool.
        tool_result = await run_tool(
            tool_name,
            arguments,
        )

        # Convert the result into text before giving it to GPT.
        tool_result_text = convert_tool_result_to_text(
            tool_result
        )

        # GPT gave this tool call a unique call_id.
        #
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
    # Send all tool results back to the response that
    # originally requested those tools.
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
        "tool": tools_used[0] if len(tools_used) == 1 else tools_used,
        "response_id": final_response.id,
    }