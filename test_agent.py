import asyncio

from agent import process_message


async def main():
    """
    Test a multi-turn conversation.

    Each message uses the response ID from the
    previous message, giving the agent memory.
    """

    # At the beginning, there is no previous response.
    previous_response_id = None

    # These messages form one continuous conversation.
    test_messages = [
        "Show me account ACC-1001.",
        "How many monthly API calls does it have left?",
        (
            "Create a support ticket for it because "
            "the database connection keeps failing."
        ),
        "What was the ticket ID?",
    ]

    for message in test_messages:
        print("\nUser:")
        print(message)

        # Pass the previous response ID into the agent.
        result = await process_message(
            user_message=message,
            previous_response_id=previous_response_id,
        )

        print("\nAgent:")
        print(result["answer"])

        print("\nTool used:")
        print(result["tool"])

        # Save the newest response ID.
        #
        # The next user message will use this ID
        # to continue the same conversation.
        previous_response_id = result["response_id"]

        print("\n" + "-" * 60)


# Start the asynchronous program.
if __name__ == "__main__":
    asyncio.run(main())