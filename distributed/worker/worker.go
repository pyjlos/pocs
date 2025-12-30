package worker

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/segmentio/kafka-go"
)

type File struct {
	Id   string `json:"id"`
	Name string `json:"name"`
	uuid string
}

func Start() {
	processed := make(map[string]bool)
	fmt.Println("Worker service starting")
	readFromKafka(processed)
}

func readFromKafka(processed map[string]bool) {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:  []string{"localhost:9092"},
		Topic:    "distributed-test-topic",
		MinBytes: 1,    // fetch as soon as data arrives
		MaxBytes: 10e6, // 10MB
	})

	defer reader.Close()

	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			log.Printf("error reading message: %v", err)
			continue
		}

		fmt.Printf("Received message:\n")
		fmt.Printf("  topic=%s partition=%d offset=%d\n",
			msg.Topic, msg.Partition, msg.Offset)

		fmt.Printf("  value=%s\n", string(msg.Value))
		// for poc purposes - just use in memory map
		id, _ := parseMessage(msg.Value)
		if _, ok := processed[id]; ok {
			fmt.Printf("File with ID %s has already been processed. Skipping...\n", id)
			continue
		} else {
			fmt.Println("Processing new file...")
			processed[id] = true
		}

		fmt.Println("Sending to worker processing...")
		fmt.Println("processed files are :", processed)
	}
}

func parseMessage(message []byte) (string, string) {
	var file File
	err := json.Unmarshal(message, &file)
	if err != nil {
		log.Printf("error unmarshaling message: %v", err)
		return "", ""
	}
	return file.Id, file.Name
}
