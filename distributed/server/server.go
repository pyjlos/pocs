package server

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/segmentio/kafka-go"

	"github.com/google/uuid"
)

type File struct {
	Id   string `json:"id"`
	Name string `json:"name"`
	uuid string
}

func Start() {
	fmt.Println("Server service starting on port 9000")

	// define handler for post endpoint
	http.HandleFunc("/files/post", post)

	// start http server on localhost:9000
	err := http.ListenAndServe(":9000", nil)
	if err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func post(writer http.ResponseWriter, request *http.Request) {
	fmt.Println("Server service posting")
	// read request body into File Struct and add uuid
	var fileToSend File

	if err := json.NewDecoder(request.Body).Decode(&fileToSend); err != nil {
		http.Error(writer, "Invalid request payload", http.StatusBadRequest)
		return
	}
	fileToSend.uuid = uuid.New().String()

	fmt.Printf("Received file to send: %+v\n", fileToSend)

	sendToKafka(fileToSend)
	writer.Write([]byte("Successfully sent message"))
}

func sendToKafka(file File) {
	topic := "distributed-test-topic"
	partition := 0
	bytesToSend, err := json.Marshal(file)

	conn, err := kafka.DialLeader(context.Background(), "tcp", "localhost:9092", topic, partition)
	if err != nil {
		log.Fatal("failed to dial leader:", err)
	}

	conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
	_, err = conn.WriteMessages(
		kafka.Message{Value: bytesToSend},
	)
	if err != nil {
		log.Fatal("failed to write messages:", err)
	}

	if err := conn.Close(); err != nil {
		log.Fatal("failed to close writer:", err)
	}
	fmt.Println("Sent message to kafka topic successfully")
}
