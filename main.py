import asyncio

from agent import process_message

#programs starts from here
async def main():
    """
    Run the Developer Support Agent as an interactive
    terminal chat application.

    The user can keep sending messages until they type:
    exit
    quit
    """

    # At the beginning, there is no previous GPT response.
    #
    # After every message, we save the newest response ID
    # so the next message continues the same conversation.
    previous_response_id = None

    print("=" * 60)
    print("Developer Support Agent")
    print("=" * 60)

    print(
        "\nAsk a question about Supabase documentation, "
        "developer accounts, support tickets, or GitHub repositories"
    )

    print("Type 'exit' to close the agent.\n")

    #keep program running and not end after one prompt
    while True: 

        # input() waits for the user to type a message.
        user_message = input("You: ").strip()

        # Ignore empty messages.
        if not user_message:
            print("Please enter a message.\n")
            continue

        # Convert the message to lowercase before checking it.
        
        if user_message.lower() in ["exit"]:
            print("\nAgent: Goodbye!")
            break

        try:
            # Send the newest message to the agent.
            #
            # We also pass the previous response ID so the
            # agent remembers the earlier conversation.
            result = await process_message(
                user_message=user_message,
                previous_response_id=previous_response_id,
            )

            # Print the agent's final natural-language answer.
            print(f"\nAgent: {result['answer']}\n")

            # Save the newest response ID.
            #
            # The next user message will use this ID to
            # continue the same conversation.
            previous_response_id = result["response_id"]

        except Exception as error:
            # Prevent the entire application from crashing
            # if one message causes an error.
            print("\nAgent: Something went wrong.")

            # Print the actual error during development
            # so we can understand and fix it.
            print(f"Error: {error}\n")


# Start the asynchronous terminal application.
if __name__ == "__main__":
    asyncio.run(main())