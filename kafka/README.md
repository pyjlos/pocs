## Kafka POC

### Commands to run
```
docker compose up -d
python3.14 -m venv venv

```

### In one terminal window
```
# starting the consumer
python3 consumer.py
```

### In another terminal window
```
starting the producer
python3 producer.py
```

### Notes
- producer -> in charge of producing new messages to a given topic
    - can use a key serializer
    - use keys to guarantee ordering across partitions
    - if there's no keys -> random order across partitions
        - however within a partition -> ordering is possible
- consumer -> in charge of reading messages from a topic
    - manually commit when done with operations to ensure idemoptency
    - auto_offset -> if latest -> only reads messages when consumer is started
        - so you probably want earliest + group_id to read the latest messages
- topics -> generally speaking topics will have multiple partitions
    - if you need to guarantee ordering across all partitions -> use a key
    - be careful of hot partitions
    - if you just want to process things as they come -> don't use a key
    - if you only have one consumer -> you can get away with one partition
    - multiple partitions really help with multiple consumers (for faster processing)