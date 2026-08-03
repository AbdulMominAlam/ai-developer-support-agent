import json
import pika


# Name of the RabbitMQ queue.
# Both the producer and worker must use the same queue name.
QUEUE_NAME = "support_ticket_queue"


def publish_support_ticket(
    account_id: str,
    category: str,
    description: str,
):
    """
    Send a support ticket request to RabbitMQ.
    """

    # Connect to the local RabbitMQ server.
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
        )
    )

    # Create a communication channel.
    channel = connection.channel()

    # Create the queue if it does not already exist.
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    # Build the message that will be sent.
    message = {
        "account_id": account_id,
        "category": category,
        "description": description,
    }

    # Publish the message to the queue.
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
    )

    print("Support ticket request sent.")

    # Close the RabbitMQ connection.
    connection.close()


# Run this file directly for testing.
if __name__ == "__main__":

    publish_support_ticket(
        account_id="ACC-1001",
        category="Authentication",
        description="Password reset email not arriving.",
    )