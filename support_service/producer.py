import json
import pika

QUEUE_NAME = "support_ticket_queue"


def publish_support_ticket(
    account_id: str,
    category: str,
    description: str,
):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )

    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
    )

    message = {
        "account_id": account_id,
        "category": category,
        "description": description,
    }

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
    )

    connection.close()

    print("Message sent!")


if __name__ == "__main__":
    publish_support_ticket(
        "ACC-1001",
        "Authentication",
        "Password reset email not arriving",
    )