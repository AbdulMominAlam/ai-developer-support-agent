import json

import pika


# Queue name.
# Both the producer and worker must use
# exactly the same queue name.
QUEUE_NAME = "support_ticket_queue"


def publish_support_ticket(
    account_id: str,
    category: str,
    description: str,
):
    """
    Send a support ticket request
    to RabbitMQ.
    """

    # Connect to the local RabbitMQ server.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
        )
    )

    # Create a communication channel.
    channel = connection.channel()

    # Create the queue if it does not exist.
    #
    # durable=True means the queue survives
    # RabbitMQ restarts.
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    # Build the message that will be sent
    # to the support worker.
    message = {
        "account_id": account_id,
        "category": category,
        "description": description,
    }

    # Send the message to RabbitMQ.
    #
    # delivery_mode=2 marks the message
    # as persistent so RabbitMQ stores it
    # on disk.
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        ),
    )

    # Close the RabbitMQ connection.
    connection.close()

    # Return a response back to the agent.
    #
    # The ticket has not been created yet.
    # It has only been placed into the queue.
    return {
        "success": True,
        "status": "queued",
        "message": (
            "The support ticket request was "
            "added to the processing queue."
        ),
    }


# Run this file directly for testing.
if __name__ == "__main__":

    result = publish_support_ticket(
        account_id="ACC-1001",
        category="Authentication",
        description="Password reset email not arriving.",
    )

    print(result)