package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"github.com/go-redis/redis"

	"go.elastic.co/apm"
	"go.elastic.co/apm/module/apmhttp"
)

const (
	listenAddr = "0.0.0.0:8000"
)

var (
	rdb = redis.NewClient(&redis.Options{Addr: os.Getenv("REDIS_URL"), Password: os.Getenv("REDIS_PWD")})
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

					// Record page view
					//
					i, err := rdb.Incr("pageviews").Result()
					if err != nil {
						apm.CaptureError(req.Context(), err).Send()
						log.Println("Redis error:", err)
						http.Error(w, "Internal Server Error", http.StatusInternalServerError)
						return
					}

					fmt.Fprintf(w, "Hello! This page has been viewed %d times.\n", i)
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
