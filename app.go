package main

import (
	"io"
	"log"
	"net/http"
	"os"

	"go.elastic.co/apm/module/apmhttp"
)

const (
	listenAddr = "0.0.0.0:8000"
)

func main() {
	log.SetFlags(0)

	http.Handle(
		"/",
		apmhttp.Wrap(
			http.HandlerFunc(
				func(w http.ResponseWriter, req *http.Request) {
					// Handle /status
					//
					if req.URL.Path == "/status" {
						io.WriteString(w, "OK")
						return
					}

					io.WriteString(w, "Hello Elastic!\n")
				},
			),
		),
	)

	log.Printf("Server starting at %s...", listenAddr)
	if err := http.ListenAndServe(listenAddr, nil); err != nil && err != http.ErrServerClosed {
		log.Fatal("Unable to start server")
		os.Exit(1)
	}
}
