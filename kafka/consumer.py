from kafka import KafkaConsumer


def main():
    consumer = KafkaConsumer(
        "test-topic",
        bootstrap_servers=["localhost:9092", "localhost:9093", "localhost:9094"],
        auto_offset_reset="earliest",  # default is 'latest'
        # what this means if it's set to latest is that it only reads
        # messages when the consumer is online
        group_id="test-group",  # if we don't have a group_id -> it defaults to None
        # which means that when the consumer is restarted -> it behaves like a new consumer
        # and auto_offset_reset determines where it starts
        # so in the event where
        # auto_offset_reset -> earliest and no group_id -> we will replay all messages
        # enable_auto_commit=False,  # default is True
        # auto_commit_interval_ms=1000,  # default is 5000
        # this means that every 1000ms -> it will commit the offset to the kafka broker
        # otherwise - it will commit every 5 seconds
        # generally - a manual commit is better for idempotent operations to get full control
    )
    print(f"consumer is {consumer}")
    store = {}
    while True:
        choice = input(
            "Enter in 1 to get the next message, or 2 to get the current store: "
        )
        if choice == "1":
            message = next(consumer)
            print(f"message is {message}")
            store_in_datastore(datastore=store, key=message.key, value=message.value)
            consumer.commit()  # manual commit after storing in datastore
        elif choice == "2":
            print(f"store is {store}")
        elif choice == "exit":
            break


def store_in_datastore(datastore: dict, key, value):
    # mimics a external datastore
    # in prod -> this is probably something not in memory
    # and the key is something that's not a uuid
    if key not in datastore:
        datastore[key] = value
        return True
    print(f"Key {key} already exists in datastore")
    return False


if __name__ == "__main__":
    main()
