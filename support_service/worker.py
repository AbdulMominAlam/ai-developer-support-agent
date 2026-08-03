import json
import pika


# Queue name.
# Must match the producer.
QUEUE_NAME = "support_ticket_queue"


def callback(
    channel,
    method,
    properties,
    body,
):
    """
    Called automatically whenever
    a new message arrives.
    """

    # Convert the JSON message back
    # into a Python dictionary.
    ticket = json.loads(body)

    print("\nReceived Support Ticket")
    print(ticket)

    # Tell RabbitMQ that the message
    # has been processed successfully.
    channel.basic_ack(
        delivery_tag=method.delivery_tag,
    )


# Connect to RabbitMQ.
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
    )
)

# Create a communication channel.
channel = connection.channel()

# Make sure the queue exists.
channel.queue_declare(
    queue=QUEUE_NAME,
    durable=True,
)

# Register the callback function.
# RabbitMQ will call it whenever
# a new message arrives.
channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
)

print("Waiting for support ticket requests...")

# Keep listening forever.
channel.start_consuming()