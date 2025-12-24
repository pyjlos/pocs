from kafka import KafkaProducer
import uuid


def main():
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092", "localhost:9093", "localhost:9094"],
        client_id="test-producer",
        key_serializer=str.encode,
    )
    print(f"producer is {producer}")

    while True:
        message = get_message_input()
        if message.lower() == "exit":
            break
        print(f"Sending message: {message}")
        producer.send(
            topic="test-topic",
            key=str(uuid.uuid4()),
            value=bytes(message, encoding="utf-8"),
        )
        producer.flush()  # block until all messages are sent


def get_message_input() -> str:
    message = input("Enter the message: ")
    return message


if __name__ == "__main__":
    main()
