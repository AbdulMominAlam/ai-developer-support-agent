import asyncio
import json

import pika

from clients.mcp_client import call_mcp_tool


# Both producer and worker must use the same queue name.
QUEUE_NAME = "support_ticket_queue"


async def create_ticket(ticket):
    """
    Call the existing MCP support-ticket tool.

    The worker receives the request from RabbitMQ,
    then sends it to the Developer Support MCP server.
    """

    result = await call_mcp_tool(
        "create_support_ticket",
        {
            "account_id": ticket["account_id"],
            "category": ticket["category"],
            "description": ticket["description"],
        },
    )

    return result


def callback(
    channel,
    method,
    properties,
    body,
):
    """
    Run whenever RabbitMQ delivers a ticket request.
    """

    # Convert the RabbitMQ JSON message
    # into a Python dictionary.
    ticket = json.loads(
        body.decode("utf-8")
    )

    print("\nReceived support-ticket request:")
    print(ticket)

    try:
        # call_mcp_tool() is asynchronous,
        # so run it through asyncio.
        result = asyncio.run(
            create_ticket(ticket)
        )

        print("\nTicket created successfully:")
        print(result)

        # Remove the message from the queue only
        # after the ticket was created successfully.
        channel.basic_ack(
            delivery_tag=method.delivery_tag,
        )

    except Exception as error:
        print("\nTicket creation failed:")
        print(error)

        # Return the message to the queue
        # so it can be attempted again.
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )


def main():
    """
    Connect to RabbitMQ and keep waiting
    for support-ticket requests.
    """

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
        )
    )

    channel = connection.channel()

    # Create the queue if it does not exist.
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    # Give this worker one unacknowledged
    # message at a time.
    channel.basic_qos(
        prefetch_count=1,
    )

    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=callback,
    )

    print(
        "Support worker is waiting "
        "for ticket requests..."
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()