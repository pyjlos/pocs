package main

import (
	"distributed/server"
	"distributed/worker"
	"flag"
	"fmt"
)

func main() {
	fmt.Println("Distributed system main entry point")
	serverPtr := flag.String("server", "", "Flag for server or worker: use server for server, worker for worker")
	flag.Parse()

	if serverPtr == nil || (*serverPtr != "server" && *serverPtr != "worker") {
		fmt.Println("Please provide a valid flag: server for server, worker for worker")
		return
	}

	if *serverPtr == "server" {
		server.Start()
	}

	if *serverPtr == "worker" {
		worker.Start()
	}
}
