## Example of a distributed system
- go-api, kafka, and then worker
```
Client
  │
  ▼
Go HTTP API
  │
  ▼
Event Queue (Kafka)
  │
  ▼
Worker Service (Go)
  │
  ├── In memory map
  └── DLQ

For PoC purposes - we'll just use an in-memory map

In real world situations, use an external data store like postgres or redis
```

## Starting kafka
```
docker compose up -d
```

## Starting Server
```
go run main.go --server=server
```

## Starting Worker
```
go run main.go --server=worker
```

## Example Curls
```
curl localhost:9000/files/post --header "Content-Type: application/json" --data '{"id":"1","name":"test-file-name"}'
# the first response should be something along the lines of "Processing new file"


curl localhost:9000/files/post --header "Content-Type: application/json" --data '{"id":"1","name":"test-file-name"}'
# This second curl of the same id should response back with 
```